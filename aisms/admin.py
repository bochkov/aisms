# coding: utf-8
from django.contrib import admin
from aisms import models


class ImageInline(admin.StackedInline):
    model = models.Image


class MeasureAdmin(admin.ModelAdmin):
    inlines = [ImageInline]


admin.site.register(models.Organization)
admin.site.register(models.Department)
admin.site.register(models.Measure, MeasureAdmin)
admin.site.register(models.Document)
admin.site.register(models.Passport)
admin.site.register(models.Journal)
admin.site.register(models.Work)
