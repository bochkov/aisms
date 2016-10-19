from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login, logout
from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from aisms import views, models

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),

    url(r'^organization/(?P<pk>\d+)/$', login_required(DetailView.as_view(
        model=models.Organization, template_name='models/organization/detail.html')),
        name='organization_detail'),
    url(r'^organization/$', login_required(ListView.as_view(
        model=models.Organization, template_name='models/organization/list.html')),
        name='organization_list'),
    url(r'^organization/add/$', views.add_organization, name='add_organization'),

    url(r'^department/(?P<pk>\d+)/$', login_required(DetailView.as_view(
        model=models.Department, template_name='models/department/detail.html')),
        name='department_detail'),
    url(r'^department/$', login_required(ListView.as_view(
        model=models.Department, template_name='models/department/list.html')),
        name='department_list'),
    url(r'^department/add/$', views.add_department, name='add_department'),

    url(r'^measure/(?P<pk>\d+)/$', DetailView.as_view(
        model=models.Measure, template_name='models/measure/detail.html'),
        name='measure_detail'),
    url(r'^measure/$', ListView.as_view(
        model=models.Measure, template_name='models/measure/list.html'),
        name='measure_list'),
    url(r'^measure/add/$', views.add_measure, name='add_measure'),

    url(r'^document/(?P<pk>\d+)/$', DetailView.as_view(
        model=models.Document, template_name='models/document/detail.html'),
        name='document_detail'),
    url(r'^document/$', ListView.as_view(
        model=models.Document, template_name='models/document/list.html'),
        name='document_list'),
    url(r'^document/add/$', views.add_document, name='add_document'),

    url(r'^passport/(?P<pk>\d+)/$', DetailView.as_view(
        model=models.Passport, template_name='models/passport/detail.html'),
        name='passport_detail'),
    url(r'^passport/$', ListView.as_view(
        model=models.Passport, template_name='models/passport/list.html'),
        name='passport_list'),
    url(r'^passport/add/$', views.add_passport, name='add_passport'),

    url(r'^work/reception/$', views.work_reception, name='work_reception'),
    url(r'^work/verification/(?P<pk>\d+)/$',
        login_required(views.VerificationDocumentView.as_view(views.FORMS)),
        name='work_verification'),
    url(r'^work/verification/list/$', login_required(ListView.as_view(
        queryset=models.Journal.objects.filter(passport__status__in=[0, 2]).order_by("-date"),
        template_name='work/verification_list.html')),
        name='work_verification_list'),
    url(r'^work/repair/(?P<pk>\d+)/$', views.work_repair, name='work_repair'),
    url(r'^work/repair/list/$', login_required(ListView.as_view(
        queryset=models.Journal.objects.filter(passport__status=3).order_by("-date"),
        template_name='work/repair_list.html')),
        name='work_repair_list'),
    url(r'^work/issue/list/$', login_required(ListView.as_view(
        queryset=models.Passport.objects.filter(status=5), template_name='work/issue_list.html')),
        name='work_issue_list'),
    url(r'^work/issue/(?P<pk>\d+)/$', views.work_issue, name='work_issue'),

    url(r'^report/journal/$', views.report_journal, name='report_journal'),
    url(r'^report/works/type/$', views.report_works_type, name='report_works_type'),
    url(r'^report/works/performer/$', views.report_works_performer, name='report_works_performer'),

    url(r'^report/done/$', ListView.as_view(
        queryset=models.Passport.objects.filter(status=5), template_name='report/done.html'),
        name='report_done'),
    url(r'^report/debt/$', views.report_debt, name='report_debt'),
    url(r'^report/plan/$', views.report_plan, name='report_plan'),
    url(r'^report/plan/(?P<organization>\d+)/$', views.report_plan_detail, name='report_plan_detail'),
    url(r'^report/plan/print/(?P<organization>\d+)/$', views.report_plan_detail, {'to_print': True}, name='print_plan'),

    url(r'^number_search/$', views.number_search, name='number_search'),

    url(r'^interval_by_type/$', views.interval_by_type),

    url(r'^login/$', login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
)
