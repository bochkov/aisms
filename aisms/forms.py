# coding=utf-8
import datetime
from django import forms
from aisms_project.aisms import models


class AddMeasure(forms.ModelForm):
    class Meta:
        model = models.Measure
        exclude = ('documents',)


class AddPassport(forms.ModelForm):
    class Meta:
        model = models.Passport


class AddPeople(forms.ModelForm):
    class Meta:
        model = models.People


INPUT = ['%d.%m.%Y']


class Reception(forms.Form):
    date = forms.DateField(input_formats=INPUT,
                           label='Дата приема',
                           initial=datetime.datetime.now())
    department = forms.ModelChoiceField(label="Подразделение",
                                        queryset=models.Department.objects.all())
    measure = forms.ModelChoiceField(label="СИ",
                                     queryset=models.Measure.objects.all().order_by("type"))
    number = forms.CharField(label="Зав.номер")
    in_pass = forms.CharField(label="Сдал")
    in_took = forms.CharField(label="Принял")


class ReportPeriod(forms.Form):
    delta = datetime.timedelta(days=30)
    from_date = forms.DateField(input_formats=INPUT,
                                label='С:',
                                initial=datetime.datetime.now() - delta)
    to_date = forms.DateField(input_formats=INPUT,
                              label="По:",
                              initial=datetime.datetime.now())

    class Meta:
        abstract = True


class ReportPeriodVerification(ReportPeriod):
    performer = forms.ModelChoiceField(label="Исполнитель",
                                       queryset=models.Verificator.objects.all(),
                                       required=False)


class ReportPeriodRepair(ReportPeriod):
    performer = forms.ModelChoiceField(label="Исполнитель",
                                       queryset=models.Repairmen.objects.all(),
                                       required=False)
