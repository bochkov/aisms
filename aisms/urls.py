from django.conf.urls.defaults import patterns, url
from django.contrib.auth.views import login, logout
from aisms_project.aisms import views

urlpatterns = patterns('',
                       url(r'^$', views.index),
                       url(r'add/(?P<entity>\w+)/$', views.add_entity),
                       url(r'journal/(?P<name>\w+)/$', views.journal),
                       url(r'journal/(?P<name>\w+)/archive/$', views.journal_archive),
                       url(r'work/reception/$', views.work_reception),
                       url(r'work/verification/$', views.work_verification),
                       url(r'work/repair/$', views.work_repair),
                       url(r'work/issue/$', views.work_issue),
                       url(r'stats/$', views.stats),
                       url(r'report/measure/$', views.report_measure),
                       url(r'report/measure/(?P<id>\d+)/$', views.report_measure),
                       url(r'report/department/$', views.report_department),
                       url(r'report/department/(?P<id>\d+)/$', views.report_department),
                       url(r'report/passport/(?P<id>\d+)/$', views.report_passport),
                       url(r'report/passport/(?P<id>\d+)/edit/$', views.report_passport_edit),
                       url(r'report/period/(?P<work>\w+)/$', views.report_period),
                       url(r'report/done/$', views.report_done),
                       url(r'report/plan/$', views.report_plan),
                       url(r'report/debt/$', views.report_debt),
                       url(r'accounts/login/$', login, {'template_name': 'aisms/login.html'}),
                       url(r'accounts/logout/$', logout, {'template_name': '', 'next_page': '/'}),
                       )
