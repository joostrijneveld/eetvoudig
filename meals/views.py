from django.shortcuts import render, redirect
from meals.models import Meal, Wbw_list, Participant, Participation
from meals.forms import MealForm, WbwListsForm, ParticipationForm, BystanderForm
from django.http import HttpResponse
from django.conf import settings

from bs4 import BeautifulSoup
import requests


def meal(request):
    context = {}
    context['lists_form'] = WbwListsForm()
    try:
        meal = context['meal'] = Meal.objects.get(completed=False)
        if 'update' in request.POST:
            form = MealForm(request.POST, instance=meal)
            if form.is_valid():
                form.save()
            return redirect('meal')
        if 'participate' in request.POST:
            pk = int(request.POST['participations'])
            participation = Participation.objects.get(pk=pk)
            meal.participants.add(participation.participant)
            meal.save()
            return redirect('meal')
        if 'bystand' in request.POST:
            pk = int(request.POST['participations'])
            form = BystanderForm(request.POST)
            participation = Participation.objects.get(pk=pk)
            form.instance.participant = participation.participant
            form.save()
            meal.bystanders.add(form.instance)
            meal.save()
            return redirect('meal')
        if 'abort' in request.POST:
            meal.delete()
            return redirect('meal')

        qs = Participation.objects.filter(wbw_list=meal.wbw_list)
        context['participation_form'] = ParticipationForm()
        context['bystander_form'] = BystanderForm()
        context['participation_form'].fields['participations'].queryset = qs
        context['form'] = MealForm(instance=meal)
        context['form'].fields['payer'].queryset = qs
        context['eaters'] = eaters = []
        for p in meal.participants.all():
            participation = Participation.objects.get(participant=p,
                                                      wbw_list=meal.wbw_list)
            eaters.append({'participation':participation, 'participant':p})
        for b in meal.bystanders.all():
            participation = Participation.objects.get(participant=b.participant,
                                                      wbw_list=meal.wbw_list)
            eaters.append({'participation':participation, 'bystander':b})
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
        Participation.objects.filter(wbw_list=wbw_list).delete()
        for uid, name in userdata:
            participant, _ = Participant.objects.get_or_create(wbw_id=uid)
            p = Participation(wbw_list=wbw_list, participant=participant)
            p.name = name
            p.save()
    return redirect('meal')


def _create_wbw_session():
    session = requests.Session()
    payload = {'action': 'login', 'username': settings.WBW_EMAIL,
               'password': settings.WBW_PASSWORD, 'login_submit': 'Inloggen'}
    response = session.post('https://wiebetaaltwat.nl', payload)
    return (session, response)
