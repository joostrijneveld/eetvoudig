from django.forms import ModelForm, widgets
import django.forms as forms
from meals.models import Meal, Wbw_list, Bystander, Participation


class EuroWidget(widgets.NumberInput):

    def render(self, name, value, attrs=None):
        return ('<div class="input-group">\
                 <span class="input-group-addon">€-cent</span>' +
                super(EuroWidget, self).render(name, value, attrs) +
                '</div>')

    def value_from_datadict(self, data, files, name):
        return data[name]


class ParticipationForm(forms.Form):
    participations = forms.ModelChoiceField(label='Deelnemer',
                                            queryset=Participation.objects.all())

    def __init__(self, *args, **kwargs):
        wbw_list = kwargs.pop('wbw_list')
        forms.Form.__init__(self, *args, **kwargs)
        qs = Participation.objects.filter(wbw_list=wbw_list)
        self.fields['participations'].queryset = qs


class BystanderForm(ModelForm):
    class Meta:
        model = Bystander
        fields = ['name']
        labels = {'name': 'Naam mee-eter'}


class MealForm(ModelForm):
    class Meta:
        model = Meal
        fields = ['description', 'price']
        labels = {'description': 'Toelichting',
                  'price': 'Prijs'}
        widgets = {'price': EuroWidget()}

    payer = forms.ModelChoiceField(label='Betaler',
                                   queryset=Participation.objects.all(),
                                   required=False)

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        meal = kwargs['instance']
        participations = Participation.objects.filter(wbw_list=meal.wbw_list)
        self.fields['payer'].queryset = participations
        if meal.payer:
            payer = Participation.objects.get(wbw_list=meal.wbw_list,
                                              participant=meal.payer)
            self.fields['payer'].initial = payer

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)

        if self.cleaned_data['payer']:
            instance.payer = self.cleaned_data['payer'].participant
        else:
            instance.payer = None

        if commit:
            instance.save()
        return instance


class WbwListsForm(forms.Form):
    wbw_lists = forms.ModelChoiceField(queryset=Wbw_list.objects.all().order_by('name'))
