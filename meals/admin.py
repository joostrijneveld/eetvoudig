from django.contrib import admin
from meals.models import Meal, Participant, Bystander, Wbw_list

admin.site.register(Meal)
admin.site.register(Participant)
admin.site.register(Bystander)
admin.site.register(Wbw_list)
