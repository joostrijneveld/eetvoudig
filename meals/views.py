from django.shortcuts import render
from meals.models import Meal, Wbw_list, Participant, Participation
from django.http import HttpResponse
from django.conf import settings

from bs4 import BeautifulSoup
import requests


def meal(request):
    context = {}
    try:
        context['meal'] = Meal.objects.get(completed=False)
    except Meal.DoesNotExist:
        if 'startmeal' in request.POST:
            context['meal'] = Meal()
            context['meal'].save()
    return render(request, 'meals/meal.html', context)


def update_lists(request):
    session = requests.Session()
    payload = {'action': 'login', 'username': settings.WBW_EMAIL,
               'password': settings.WBW_PASSWORD, 'login_submit': 'Inloggen'}
    response = session.post('https://wiebetaaltwat.nl', payload)
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
    return HttpResponse('Done updating')
