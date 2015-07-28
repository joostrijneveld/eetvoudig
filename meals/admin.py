from django.contrib import admin
from meals.models import Meal, Participant, Bystander, Wbw_list, Participation


class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 0


class Wbw_listAdmin(admin.ModelAdmin):
    inlines = (ParticipationInline, )

admin.site.register(Meal)
admin.site.register(Participant)
admin.site.register(Bystander)
admin.site.register(Wbw_list, Wbw_listAdmin)
