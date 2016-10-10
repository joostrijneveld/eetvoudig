from django.db import models


class Wbw_list(models.Model):
    list_id = models.CharField(unique=True, max_length=40)
    name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Participant(models.Model):
    wbw_list = models.ManyToManyField(Wbw_list, through='Participation')
    wbw_id = models.CharField(unique=True, max_length=40)


class Participation(models.Model):
    name = models.CharField(max_length=200)
    wbw_list = models.ForeignKey(Wbw_list)
    participant = models.ForeignKey(Participant)

    def __str__(self):
        return self.name


class Bystander(models.Model):
    name = models.CharField(max_length=200)
    participant = models.ForeignKey(Participant)


class Meal(models.Model):
    price = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    description = models.CharField(max_length=200, blank=True)

    wbw_list = models.ForeignKey(Wbw_list, null=True)
    participants = models.ManyToManyField(Participant, blank=True)
    bystanders = models.ManyToManyField(Bystander, blank=True)
    payer = models.ForeignKey(Participant, null=True, blank=True, related_name='paymeal')
