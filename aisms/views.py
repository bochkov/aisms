# coding=utf-8
import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from aisms_project.aisms import models, forms


def norm_date(string):
    return datetime.datetime.strptime(string, "%d.%m.%Y").strftime("%Y-%m-%d")


def change_status(passport, status):
    objects = models.Status.objects.all()
    for i in objects:
        if i.get_status_display() == status:
            passport.status = i
            passport.save()


def add_work(passport, worktype, performer, date, organization_id, result):
    objects = models.Worktype.objects.all()
    for i in objects:
        if i.get_worktype_display() == worktype:
            organization = models.Organization.objects.get(id=organization_id)
            work = models.Work(passport=passport, worktype=i,
                               performer=performer, date=norm_date(date),
                               organization=organization, result=result)
            work.save()


def index(request):
    return render_to_response('aisms/base.html', None,
                              context_instance=RequestContext(request))


@login_required
def add_entity(request, entity):
    if entity == 'measure':
        model = forms.AddMeasure
    elif entity == 'passport':
        model = forms.AddPassport
    elif entity == 'people':
        model = forms.AddPeople
    else:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = model(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/add/' + entity + '/')

    else:
        form = model()

    return render_to_response('aisms/add_base.html', locals(),
                              context_instance=RequestContext(request))


@login_required
def work_issue(request):
    if request.method == 'POST':
        _id = request.POST.get('id')
        out_date = request.POST.get('out_date')
        out_pass = request.POST.get('out_pass')
        out_took = request.POST.get('out_took')
        notes = request.POST.get('notes')

        j_recept = models.JournalReception.objects.get(id=_id)
        j_recept.out_date = norm_date(out_date)
        j_recept.out_pass = out_pass
        j_recept.out_took = out_took
        j_recept.notes = notes
        j_recept.is_active = False
        j_recept.save()

        return HttpResponseRedirect('/work/issue/')

    else:
        records = models.JournalReception.objects.filter(is_active=True,
                                                         is_done=True).order_by('-in_date')

    return render_to_response('aisms/work_issue.html', locals(),
                              context_instance=RequestContext(request))


@login_required
def work_repair(request):
    if request.method == 'POST':
        _id = request.POST.get('id')
        repairmen = request.POST.get('repairmen')
        result = request.POST.get('result')
        out_date = request.POST.get('out_date')
        notes = request.POST.get('notes')

        j_repair = models.JournalRepair.objects.get(id=_id)
        j_repair.repairmen = models.Repairmen.objects.get(id=repairmen)
        j_repair.result = True if result == 'True' else False
        j_repair.out_date = norm_date(out_date)
        j_repair.notes = notes
        j_repair.is_active = False
        j_repair.save()

        add_work(j_repair.passport, u'Ремонт', j_repair.repairmen,
                 out_date, 1, j_repair.result)

        if j_repair.result:
            change_status(j_repair.passport, u'Поверка')
            j_verif = models.JournalVerification(passport=j_repair.passport, in_date=j_repair.out_date)
            j_verif.save()

        else:
            change_status(j_repair.passport, u'Списано')
            j_recept = models.JournalReception.objects.get(is_active=True, passport=j_repair.passport)
            j_recept.is_done = True
            j_recept.save()

        return HttpResponseRedirect('/work/repair/')

    else:
        records = models.JournalRepair.objects.filter(is_active=True).order_by('-in_date')
        repairmen = models.Repairmen.objects.all()

    return render_to_response('aisms/work_repair.html', locals(),
                              context_instance=RequestContext(request))


@login_required
def work_verification(request):
    if request.method == 'POST':
        _id = request.POST.get('id')
        worktype = request.POST.get('worktype')
        verificator = request.POST.get('verificator')
        result = request.POST.get('result')
        out_date = request.POST.get('out_date')
        notes = request.POST.get('notes')

        j_verif = models.JournalVerification.objects.get(id=_id)
        j_verif.verificator = models.Verificator.objects.get(id=verificator)
        j_verif.result = True if result == 'True' else False
        j_verif.out_date = norm_date(out_date)
        j_verif.notes = notes
        j_verif.is_active = False
        j_verif.save()

        add_work(j_verif.passport, worktype, j_verif.verificator,
                 out_date, 1, j_verif.result)

        if j_verif.result:
            change_status(j_verif.passport, u'Эксплуатация')
            j_recept = models.JournalReception.objects.get(is_active=True,
                                                           passport=j_verif.passport,
                                                           in_date=j_verif.in_date)
            j_recept.is_done = True
            j_recept.save()
        else:
            change_status(j_verif.passport, u'Ремонт')
            j_repair = models.JournalRepair(passport=j_verif.passport,
                                            in_date=norm_date(out_date), reason=notes)
            j_repair.save()

        return HttpResponseRedirect('/work/verification/')

    else:
        records = models.JournalVerification.objects.filter(is_active=True)
        verificators = models.Verificator.objects.all()
        worktypes = models.Worktype.objects.all()

    return render_to_response('aisms/work_verification.html', locals(),
                              context_instance=RequestContext(request))


@login_required
def work_reception(request):
    if request.method == 'POST':
        form = forms.Reception(request.POST)
        if form.is_valid():
            date = request.POST.get('date')
            department = request.POST.get('department')
            measure = request.POST.get('measure')
            number = request.POST.get('number')
            in_pass = request.POST.get('in_pass')
            in_took = request.POST.get('in_took')

            try:
                passport = models.Passport.objects.get(number=number,
                                                       measure=models.Measure.objects.get(id=measure))
            except models.Passport.DoesNotExist:
                passport = models.Passport(number=number,
                                           measure=models.Measure.objects.get(id=measure),
                                           department=models.Department.objects.get(id=department),
                                           status=models.Status.objects.get(id=1))
                passport.save()

            try:
                j_recept = models.JournalReception.objects.get(passport=passport)
            except models.JournalReception.DoesNotExist:
                j_recept = models.JournalReception(passport=passport,
                                                   in_date=norm_date(date), in_pass=in_pass,
                                                   in_took=in_took)
                j_recept.save()

            try:
                j_verif = models.JournalVerification.objects.get(passport=passport)
            except models.JournalVerification.DoesNotExist:
                j_vefif = models.JournalVerification(passport=passport,
                                                     in_date=norm_date(date))
                j_vefif.save()

            change_status(passport, u'Поверка')

            return HttpResponseRedirect('/work/reception/')

    else:
        form = forms.Reception()

    return render_to_response('aisms/work_reception.html', locals(),
                              context_instance=RequestContext(request))


def get_journal(name, active):
    if name == 'reception':
        template = 'aisms/journal_reception.html'
        objects = models.JournalReception.objects.filter(is_active=active)

    elif name == 'verification':
        template = 'aisms/journal_verification.html'
        objects = models.JournalVerification.objects.filter(is_active=active)
        if not active:
            for i in objects:
                i.performer = models.Verificator.objects.get(pk=i.verificator)

    elif name == 'repair':
        template = 'aisms/journal_repair.html'
        objects = models.JournalRepair.objects.filter(is_active=active)
        if not active:
            for i in objects:
                i.performer = models.Repairmen.objects.get(pk=i.repairmen)

    else:
        return HttpResponseRedirect('/')

    return template, {'object_list': objects}


@login_required
def journal_archive(request, name):
    j = get_journal(name, False)
    return render_to_response(j[0], j[1],
                              context_instance=RequestContext(request))


@login_required
def journal(request, name):
    j = get_journal(name, True)
    return render_to_response(j[0], j[1],
                              context_instance=RequestContext(request))


def report_measure(request, _id=None):
    if id is not None:
        measure = models.Measure.objects.get(id=_id)

    elif request.method == 'POST':
        q = request.POST.get('q')
        if q:
            qset = (
                Q(name__icontains=q) |
                Q(type__icontains=q)
            )
            measure_list = models.Measure.objects.filter(qset)

        else:
            measure_list = []

    else:
        measure_list = models.Measure.objects.all()

    return render_to_response('aisms/report_measure.html', locals(),
                              context_instance=RequestContext(request))


def report_department(request, _id=None):
    if id is not None:
        department = models.Department.objects.get(id=_id)
        try:
            measures = models.Passport.objects.filter(department=department).order_by('measure')
        except models.Passport.DoesNotExist:
            measures = []

    else:
        deps = models.Department.objects.all()

    return render_to_response('aisms/report_department.html', locals(),
                              context_instance=RequestContext(request))


def report_passport(request, _id=None):
    if id is not None:
        passport = models.Passport.objects.get(id=_id)
        works = models.Work.objects.filter(passport=passport).order_by('date')

    return render_to_response('aisms/report_passport.html', locals(),
                              context_instance=RequestContext(request))


@login_required
def report_passport_edit(request, _id=None):
    return HttpResponseRedirect('/report/passport/' + _id + '/')


@login_required
def report_period(request, work):
    if work == 'verification':
        form = forms.ReportPeriodVerification
        model = models.JournalVerification
    elif work == 'repair':
        form = forms.ReportPeriodRepair
        model = models.JournalRepair
    else:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = form(request.POST)
        if form.is_valid():
            from_date = norm_date(request.POST.get('from_date'))
            to_date = norm_date(request.POST.get('to_date'))
            performer = request.POST.get('performer', '')

            result = model.objects.report(from_date, to_date, performer)
    else:
        form = form()

    return render_to_response('aisms/report_period.html', locals(),
                              context_instance=RequestContext(request))


def report_done(request):
    results = models.JournalReception.objects.filter(is_active=True, is_done=True)
    return render_to_response('aisms/report_done.html', locals(),
                              context_instance=RequestContext(request))


@login_required
def report_plan(request):
    if request.method == 'POST':
        _id = request.POST.get('organization', None)
        result = models.Passport.objects.plan(_id)

    organization = models.Organization.objects.all()
    return render_to_response('aisms/report_plan.html', locals(),
                              context_instance=RequestContext(request))


def report_debt(request):
    passport = models.Passport.objects.filter(status__status=1)  # В эксплуатации
    results = []
    for p in passport:
        interval = p.measure.interval
        work = models.Work.objects.filter(passport=p).latest('date')
        loose = datetime.datetime.today() - work.date
        if loose > datetime.timedelta(days=interval * 30):
            loose -= datetime.timedelta(days=interval * 30)
            p.loose = loose.days
            results.append(p)

    return render_to_response('aisms/report_debt.html', {'results': results},
                              context_instance=RequestContext(request))


@login_required
def stats(request):
    count_all = models.Passport.objects.exclude(status__status=5).count()
    count_work = models.Passport.objects.exclude(status__status__in=(4, 5)).count()
    count_not_in_use = models.Passport.objects.filter(status__status=4).count()
    count_in_metr = models.Passport.objects.filter(status__status__in=(2, 3)).count()

    by_years = models.by_years()
    by_deps = models.Passport.objects.by_deps()
    return render_to_response('aisms/stats.html', locals(),
                              context_instance=RequestContext(request))
