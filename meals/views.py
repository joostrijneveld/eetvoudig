from django.shortcuts import render, redirect
from meals.models import Meal, Wbw_list, Participant, Participation, Bystander
from meals.forms import MealForm, WbwListsForm, ParticipationForm, BystanderForm
from django.conf import settings
from django.contrib import messages
from django.utils.timezone import localtime
from datetime import datetime

from bs4 import BeautifulSoup
import requests
from itertools import chain
from collections import defaultdict


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
                date = datetime.strftime(localtime(meal.date), "%d-%m-%Y")
                payload = defaultdict(lambda: 0,
                                      {'action': 'add_transaction',
                                       'lid': meal.wbw_list.list_id,
                                       'payment_by': meal.payer.wbw_id,
                                       'description': meal.description,
                                       'date': date,
                                       'amount': meal.price / 100,
                                       'submit_add': 'Verwerken'})
                for p in chain(meal.participants.all(),
                               [b.participant for b in meal.bystanders.all()]):
                    payload['factor[{}]'.format(p.wbw_id)] += 1
                session.post('https://wiebetaaltwat.nl/index.php', payload)
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
    soup = BeautifulSoup(response.text, 'html.parser')
    lists = [x.a for x in soup.tbody.findAll('td') if x.a is not None]
    listdata = [(x.attrs['href'][15:-13], x.text) for x in lists]
    for list_id, list_name in listdata:
        wbw_list, _ = Wbw_list.objects.get_or_create(list_id=list_id)
        wbw_list.name = list_name
        wbw_list.save()
        url = 'https://wiebetaaltwat.nl/index.php?lid='+list_id+'&page=members'
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        trs = soup.tbody.findAll('tr')
        userdata = [(tr.attrs['id'][7:], tr.td.span.text) for tr in trs]
        userdata = [(uid, name) for uid, name in userdata if uid != settings.WBW_UID]
        Participation.objects.filter(wbw_list=wbw_list).delete()
        for uid, name in userdata:
            participant, _ = Participant.objects.get_or_create(wbw_id=uid)
            p = Participation(wbw_list=wbw_list, participant=participant)
            p.name = name
            p.save()
        if len(userdata) == 0:
            wbw_list.delete()
    return redirect('meal')


def _create_wbw_session():
    session = requests.Session()
    payload = {'action': 'login', 'username': settings.WBW_EMAIL,
               'password': settings.WBW_PASSWORD, 'login_submit': 'Inloggen'}
    response = session.post('https://wiebetaaltwat.nl', payload)
    return (session, response)
