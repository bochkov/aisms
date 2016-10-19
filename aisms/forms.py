# coding: utf-8
import datetime
from django import forms
from aisms import models


class Select2(forms.Select):
    def __init__(self, attrs=None):
        if attrs is not None:
            attrs.update({'class': 'select2'})
        else:
            attrs = {'class': 'select2'}

        super(Select2, self).__init__(attrs)


class Select2Multi(forms.SelectMultiple):
    def __init__(self, attrs=None):
        if attrs is not None:
            attrs.update({'class': 'select2-mul'})
        else:
            attrs = {'class': 'select2-mul'}

        super(Select2Multi, self).__init__(attrs)


class AddOrganizationForm(forms.ModelForm):
    class Meta:
        model = models.Organization
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3})
        }


class AddDepartmentForm(forms.ModelForm):
    class Meta:
        model = models.Department
        widgets = {
            'organization': Select2,
        }


class AddMeasureForm(forms.ModelForm):
    class Meta:
        model = models.Measure
        widgets = {
            'features': forms.Textarea(attrs={'rows': 3}),
            'document': Select2Multi,
            'interval': Select2,
            'area': Select2,
        }


class AddDocumentForm(forms.ModelForm):
    class Meta:
        model = models.Document
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3})
        }


class AddPassportForm(forms.ModelForm):
    # TODO organization and department check
    class Meta:
        model = models.Passport
        widgets = {
            'manufacture_date': forms.DateInput(format='%d.%m.%Y', attrs={'class': 'datepicker'}),
            'measure': Select2,
            'organization': Select2,
            'department': Select2,
            'status': Select2,
        }


class ReceptionForm(forms.ModelForm):
    class Meta:
        model = models.Journal
        widgets = {
            'date': forms.DateTimeInput(format='%d.%m.%Y %H:%M', attrs={'class': 'datetimepicker'}),
            'passport': Select2,
        }
        exclude = ("journal_out",)


class IssueForm(forms.ModelForm):
    class Meta:
        model = models.JournalOut
        exclude = ("journal",)


class WorkForm(forms.ModelForm):
    class Meta:
        abstract = True
        model = models.Work
        widgets = {
            'date': forms.DateTimeInput(format='%d.%m.%Y %H:%M', attrs={'class': 'datetimepicker'}),
            'tipo': Select2,
        }
        exclude = ("passport", "document")


class VerificationForm(WorkForm):
    create_doc = forms.BooleanField(required=False, initial=True, label='Создать документ')

    def __init__(self, *args, **kwargs):
        super(VerificationForm, self).__init__(*args, **kwargs)
        self.fields['tipo'].choices = models.VERIFICATION_WORK


class RepairForm(WorkForm):

    def __init__(self, *args, **kwargs):
        super(RepairForm, self).__init__(*args, **kwargs)
        self.fields['tipo'].choices = models.REPAIR_WORK


class DocumentForm(forms.Form):
    number = forms.CharField(max_length=10, initial=1)
    last_verif = forms.CharField(max_length=100, required=False)


class ReportPerformerForm(forms.Form):
    performer = forms.CharField(required=False, label='Исполнитель')
    from_date = forms.DateTimeField(
        label='С',
        initial=datetime.datetime.now() - datetime.timedelta(days=30),
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=False)
    to_date = forms.DateTimeField(
        label='По',
        initial=datetime.datetime.now() + datetime.timedelta(days=1),
        widget=forms.DateInput(attrs={'class': 'datepicker'}),
        required=False)

    def clean(self):
        super(ReportPerformerForm, self).clean()
        from_date = self.cleaned_data.get('from_date')
        to_date = self.cleaned_data.get('to_date')

        if from_date > to_date:
            raise forms.ValidationError("First time cannot be greather than second time")

        return self.cleaned_data


class PlanForm(forms.Form):
    organization = forms.ModelChoiceField(queryset=models.Organization.objects,
                                          widget=Select2, label='Для организации')
