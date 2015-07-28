from django.shortcuts import render
from meals.models import Meal


def meal(request):
    context = {}
    try:
        context['meal'] = Meal.objects.get(completed=False)
    except Meal.DoesNotExist:
        if 'startmeal' in request.POST:
            context['meal'] = Meal()
            context['meal'].save()
    return render(request, 'meals/meal.html', context)
