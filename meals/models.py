from django.db import models


class WBW_list(models.Model):
    list_id = models.IntegerField()


class Meal(models.Model):
    price = models.IntegerField(default=0)
    payer = models.ForeignKey(WBW_list, null=True)
    date = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)


class Participant(models.Model):
    wbw_list = models.ForeignKey(WBW_list)
    meal = models.ForeignKey(Meal)
    name = models.CharField(max_length=200)
