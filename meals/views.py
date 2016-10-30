import math

from django.shortcuts import render, redirect
from meals.models import Meal, Wbw_list, Participant, Participation, Bystander
from meals.forms import MealForm, WbwListsForm, ParticipationForm, BystanderForm
from django.conf import settings
from django.contrib import messages
from django.utils.timezone import localtime
from datetime import datetime

import requests
from itertools import chain


def meal(request):
    context = {}
    context['lists_form'] = WbwListsForm()
    try:
        meal = context['meal'] = Meal.objects.get(completed=False)
        context['participation_form'] = ParticipationForm(wbw_list=meal.wbw_list)
        context['bystander_form'] = BystanderForm()
        context['form'] = MealForm(instance=meal)
        context['eaters'] = eaters = []
        for p in meal.participants.all():
            participation = Participation.objects.get(participant=p,
                                                      wbw_list=meal.wbw_list)
            eaters.append({'participation': participation, 'participant': p})
        for b in meal.bystanders.all():
            participation = Participation.objects.get(participant=b.participant,
                                                      wbw_list=meal.wbw_list)
            eaters.append({'participation': participation, 'bystander': b})

        # these should probably be split into different view functions
        if 'update' in request.POST:
            context['form'] = form = MealForm(request.POST, instance=meal)
            if form.is_valid():
                form.save()
                return redirect('meal')
        elif 'participate' in request.POST:
            pk = int(request.POST['participations'])
            participation = Participation.objects.get(pk=pk)
            meal.participants.add(participation.participant)
            meal.save()
            return redirect('meal')
        elif 'bystand' in request.POST:
            pk = int(request.POST['participations'])
            form = BystanderForm(request.POST)
            participation = Participation.objects.get(pk=pk)
            form.instance.participant = participation.participant
            form.save()
            meal.bystanders.add(form.instance)
            meal.save()
            return redirect('meal')
        elif 'unbystand' in request.POST:
            pk = int(request.POST['unbystand'])
            meal.bystanders.remove(Bystander.objects.get(pk=pk))
            meal.save()
            return redirect('meal')
        elif 'unparticipate' in request.POST:
            pk = int(request.POST['unparticipate'])
            meal.participants.remove(Participant.objects.get(pk=pk))
            meal.save()
            return redirect('meal')
        elif 'abort' in request.POST:
            meal.delete()
            return redirect('meal')
        elif 'finalise' in request.POST:
            context['form'] = form = MealForm(request.POST, instance=meal)
            if form.is_valid():
                form.save()
            errors = False  # surely there's a more elegant way to do this
            if not meal.payer:
                context['form'].add_error('payer', "Wie gaat dit geintje betalen?.")
                errors = True
            if not meal.price > 0:
                context['form'].add_error('price', "Er moet wel iets te betalen vallen.")
                errors = True
            if not meal.participants.all() and not meal.bystanders.all():
                messages.error(request, "Zonder deelnemers valt er niks te verwerken.")
                errors = True
            if not errors:
                session, response = _create_wbw_session()
                date = datetime.strftime(localtime(meal.date), "%Y-%m-%d")
                desc = []
                for b in meal.bystanders.all():
                    part = Participation.objects.get(participant=b.participant,
                                                     wbw_list=meal.wbw_list)
                    desc.append("{} via {}".format(b.name, part.name))
                desc = "{} ({})".format(meal.description, ', '.join(desc))

                payload = {'expense': {
                    'payed_by_id': meal.payer.wbw_id,
                    'name': desc,
                    'payed_on': date,
                    'amount': 0,
                    'shares_attributes': []}}

                participants = list(chain(meal.participants.all(),
                                          [b.participant for b in
                                           meal.bystanders.all()]))
                amount_per_p = math.ceil(meal.price / len(participants))
                for p in participants:
                    payload['expense']['shares_attributes'].append({
                        'member_id': p.wbw_id,
                        'multiplier': 1,
                        'amount': amount_per_p
                    })
                    # Wiebetaaltwat does not like to share beyond decimals
                    # so we ensure that the total amount is the sum of parts.
                    payload['expense']['amount'] += amount_per_p

                # We must remove duplicate shares
                shares = {}
                for share in list(payload['expense']['shares_attributes']):
                    if share['member_id'] not in shares:
                        shares[share['member_id']] = share
                    else:
                        shares[share['member_id']]['multiplier'] += 1
                        # Since multiplier and amount seem to be unrelated..
                        shares[share['member_id']]['amount'] += amount_per_p
                        payload['expense']['shares_attributes'].remove(share)

                url = ('https://api.wiebetaaltwat.nl/api/lists/{}/expenses'
                       .format(meal.wbw_list.list_id))
                session.post(url,
                             json=payload,
                             headers={'Accept-Version': '1'},
                             cookies=response.cookies)
                meal.completed = True
                meal.save()
                messages.success(request, "De maaltijd is verwerkt!")
                return redirect('meal')

    except Meal.DoesNotExist:
        if 'startmeal' in request.POST:
            form = WbwListsForm(request.POST)
            if form.is_valid():
                wbw_list = Wbw_list.objects.get(pk=form.data['wbw_lists'])
                Meal(wbw_list=wbw_list).save()
                return redirect('meal')

    return render(request, 'meals/meal.html', context)


def update_lists(request):
    session, response = _create_wbw_session()
    response = session.get('https://api.wiebetaaltwat.nl/api/lists/',
                           headers={'Accept-Version': '1'},
                           cookies=response.cookies)
    data = response.json()

    Wbw_list.objects.all().delete()
    for item in data['data']:
        list_id = item['list']['id']
        list_name = item['list']['name']
        wbw_list, _ = Wbw_list.objects.get_or_create(list_id=list_id)
        wbw_list.name = list_name
        wbw_list.save()

        url = ('https://api.wiebetaaltwat.nl/api/lists/{list_id}/members'
               .format(list_id=list_id))
        response = session.get(url,
                               headers={'Accept-Version': '1'},
                               cookies=response.cookies)
        data = response.json()
        Participation.objects.filter(wbw_list=wbw_list).delete()
        for user_item in data['data']:
            uid = user_item['member']['id']
            if uid == settings.WBW_UID:
                continue
            name = user_item['member']['nickname']
            participant, _ = Participant.objects.get_or_create(wbw_id=uid)
            p = Participation(wbw_list=wbw_list, participant=participant)
            p.name = name
            p.save()
        if len(data['data']) == 0:
            wbw_list.delete()
    return redirect('meal')


def _create_wbw_session():
    session = requests.Session()
    payload = {'user': {
        'email': settings.WBW_EMAIL,
        'password': settings.WBW_PASSWORD,
        }
    }
    response = session.post('https://api.wiebetaaltwat.nl/api/users/sign_in',
                            json=payload,
                            headers={'Accept-Version': '1'})
    return session, response
