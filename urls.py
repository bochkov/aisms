from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^', include('aisms_project.aisms.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       )

if settings.DEBUG:
    urlpatterns += patterns('',
                            url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                                {'document_root': settings.MEDIA_ROOT}),
                            )
