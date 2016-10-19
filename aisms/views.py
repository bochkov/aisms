# coding: utf-8
import json
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.files import File
from django.template.defaultfilters import dictsort
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from webodt.shortcuts import render_to_response as webodt_render
from webodt.shortcuts import render_to as webodt_render_to
from aisms import forms, models


def index(request):
    measure_num = models.Measure.objects.count()
    passport_num = models.Passport.objects.count()
    passport_num_verif = models.Passport.objects.filter(status=2).count()
    passport_num_repair = models.Passport.objects.filter(status=3).count()
    return render(request, 'index.html', locals())


def base_add(request, form, template):
    f = form(request.POST or None, request.FILES or None)
    if f.is_valid():
        return redirect(f.save())

    return render(request, template, {'form': f})


@login_required
def add_organization(request):
    return base_add(request, forms.AddOrganizationForm, 'models/organization/add.html')


@login_required
def add_department(request):
    return base_add(request, forms.AddDepartmentForm, 'models/department/add.html')


@login_required
def add_measure(request):
    return base_add(request, forms.AddMeasureForm, 'models/measure/add.html')


@login_required
def add_document(request):
    return base_add(request, forms.AddDocumentForm, 'models/document/add.html')


@login_required
def add_passport(request):
    return base_add(request, forms.AddPassportForm, 'models/passport/add.html')


@login_required
def work_reception(request):
    form = forms.ReceptionForm(request.POST or None)
    form.fields['passport'].queryset = models.Passport.objects.filter(status__in=[0, 1])
    if form.is_valid():
        journal = form.save()
        journal.passport.status = 2
        journal.passport.save()
        return redirect('work_reception')

    return render(request, 'work/reception.html', {'form': form})


@login_required
def work_issue(request, pk):
    passport = get_object_or_404(models.Passport, pk=pk)
    if passport.status != 5:
        raise SystemError

    form = forms.IssueForm(request.POST or None)
    if form.is_valid():
        journal = get_object_or_404(models.Journal, journal_out=None, passport=passport)

        journal_out = form.save(commit=False)
        journal_out.journal = journal
        journal_out.save()

        journal.journal_out = journal_out
        journal.save()

        passport.status = 1
        passport.save()

        return redirect('work_issue_list')

    return render(request, 'work/issue.html', {'passport': passport, 'form': form})


@login_required
def work_repair(request, pk):
    passport = get_object_or_404(models.Passport, pk=pk)
    if passport.status != 3:
        return redirect('work_repair_list')
    form = forms.RepairForm(request.POST or None, request.FILES or None,
                            initial={'tipo': 2})
    if form.is_valid():
        work = form.save(commit=False)
        work.passport = passport
        work.save()

        if work.result is True:
            passport.status = 2
        else:
            passport.status = 4

        passport.save()
        return redirect('work_repair_list')

    return render(request, 'work/repair.html', {'form': form, 'passport': passport})


@login_required
def report_works_type(request):
    tipo = request.GET.get('type') or ""
    object_list = models.Work.objects.order_by("-date")
    if tipo is not "":
        object_list = object_list.filter(tipo=tipo)
    return render(request, 'report/works_type.html', {
        'object_list': object_list, 'type': tipo})


@login_required
def report_works_performer(request):
    form = forms.ReportPerformerForm(request.GET or None)
    object_list = None
    if form.is_valid():
        from_date = form.cleaned_data['from_date']
        to_date = form.cleaned_data['to_date']
        performer = form.cleaned_data['performer']
        object_list = models.Work.objects.all()
        if from_date:
            object_list = object_list.exclude(date__lte=from_date)
        if to_date:
            object_list = object_list.exclude(date__gte=to_date)
        if performer:
            object_list = object_list.filter(performer=performer)

    return render(request, 'report/works_performer.html', {
        'form': form, 'object_list': object_list})


@login_required
def report_journal(request):
    object_list = models.Journal.objects.order_by('-date')
    tipo = request.GET.get("type") or ""
    if tipo == "current":
        object_list = object_list.filter(journal_out=None)
    elif tipo == "archive":
        object_list = object_list.exclude(journal_out=None)

    return render(request, 'report/journal.html', {
        'object_list': object_list, 'type': tipo})


def report_debt(request):
    passports = models.Passport.objects.filter(status__in=[0, 1])
    object_list = [p for p in passports if p.is_debt()]
    return render(request, 'report/debt.html', {'object_list': object_list})


def interval_by_type(request):
    measure = get_object_or_404(models.Measure, id=request.GET.get('measure_id'))
    return HttpResponse(json.dumps({'interval': measure.interval}),
                        content_type='application/json')


def number_search(request):
    number = request.POST.get('number')
    object_list = models.Passport.objects.filter(number__icontains=number)
    return render(request, 'report/number_search.html',
                  {'object_list': object_list, 'number': number})


@login_required
def report_plan(request):
    form = forms.PlanForm(request.POST or None)
    if form.is_valid():
        org = form.cleaned_data['organization']
        return redirect('report_plan_detail', organization=org.id)

    return render(request, 'report/plan.html', {'form': form})


@login_required
def report_plan_detail(request, organization, to_print=False):
    organization = get_object_or_404(models.Organization, pk=organization)
    object_list = models.Passport.objects\
        .filter(Q(organization=organization) | Q(department__organization=organization))\
        .filter(status__in=(0, 1, 2))

    context = {'object_list': dictsort(object_list, 'measure.area'),
               'organization': organization}

    if to_print:
        filename = "graph.odt"
        return webodt_render("odt/plan.odt", context, filename=filename)

    return render(request, 'report/plan_detail.html', context)


## Verification ClassBased View

FORMS = [
    ("verification", forms.VerificationForm),
    ("document", forms.DocumentForm),
]

TEMPLATES = {
    "verification": 'work/verification.html',
    "document": 'work/document.html'
}


def save_verification(cd, passport):
    work = models.Work.objects.create(passport=passport,
                                      tipo=cd['tipo'],
                                      date=cd['date'],
                                      result=cd['result'],
                                      performer=cd['performer'],
                                      workplace=cd['workplace'])

    passport.status = 5 if work.result else 3
    passport.save()
    return work


def save_document(form_list, work):
    context = {'object': work.passport}
    for i in form_list:
        context.update(i.cleaned_data)

    document = webodt_render_to(
        "odt",
        "odt/svidetelstvo.odt" if work.result is True else "odt/izveshenie.odt",
        context)
    print work.document.__class__
    work.document.save("%s.odt" % work.document_name(), File(document))
    work.save()


class VerificationDocumentView(SessionWizardView):
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        passport = get_object_or_404(models.Passport, pk=pk)
        if passport.status not in [0, 2, 4, 5]:
            return redirect('work_verification_list')

        self.init_kwargs = kwargs.copy()
        return super(VerificationDocumentView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super(VerificationDocumentView, self).get_context_data(form=form, **kwargs)
        context.update({'passport': get_object_or_404(models.Passport, pk=self.init_kwargs.pop('pk'))})
        if self.steps.count == self.steps.index:
            context.update({'ok': True})
        return context

    def process_step(self, form):
        if 'create_doc' in form.cleaned_data:
            if form.cleaned_data['create_doc'] is False and 'document' in self.form_list:
                del self.form_list['document']
            else:
                self.form_list.update({'document': FORMS[1][1]})
        return form.data

    def done(self, form_list, **kwargs):
        passport = get_object_or_404(models.Passport, pk=kwargs['pk'])
        work = save_verification(form_list[0].cleaned_data, passport)
        if "create_doc" in form_list[0].cleaned_data:
            if form_list[0].cleaned_data['create_doc']:
                save_document(form_list, work)
        return redirect('work_verification_list')