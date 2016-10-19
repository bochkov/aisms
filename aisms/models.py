# coding: utf-8
import os
import datetime
from django.db import models
from django.utils.timezone import utc


class Organization(models.Model):
    name = models.CharField('Наименование', max_length=255, unique=True)
    full_name = models.CharField('Полное наименование', max_length=255, blank=True)
    dir_position = models.CharField('Должность руководителя', max_length=255, blank=True)
    dir_name = models.CharField('Фамилия И.О. руководителя', max_length=255, blank=True)
    address = models.TextField('Адрес организации', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s: %s" % (self.id, self.name)

    @models.permalink
    def get_absolute_url(self):
        return 'organization_detail', (self.id,)

    class Meta:
        ordering = ('id',)
        verbose_name = "Организация"
        verbose_name_plural = "Организации"


class Department(models.Model):
    name = models.CharField('Название', max_length=255)
    organization = models.ForeignKey(Organization, verbose_name='Организация')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'organization')
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'department_detail', (self.id,)


AREAS = (
    (0, 'Не определено'),
    (27, 'Измерения геометрических величин'),
    (28, 'Измерения механических величин'),
    (29, 'Измерения параметров потока, расхода, уровня, объема веществ'),
    (30, 'Измерения давления, вакуумные измерения'),
    (31, 'Измерения физико-химического состава и свойств веществ'),
    (32, 'Теплофизические и температурные измерения'),
    (33, 'Измерения времени и частоты'),
    (34, 'Измерения электротехнических и магнитных величин'),
    (35, 'Радиотехнические и радиоэлектронные измерения'),
    (36, 'Виброакустические измерения'),
    (37, 'Оптические и оптико-физические измерения'),
    (38, 'Измерения характеристик ионизирующих излучений и ядерных констант'),
    (39, 'Средства измерения медицинского назначения'),
)


INTERVALS = (
    (0, 'Не определено'), (6, '6'), (12, '12'), (18, '18'), (24, '24'),
    (36, '36'), (48, '48'), (60, '60'),
)


class Measure(models.Model):
    name = models.CharField('Наименование', max_length=255)
    tipo = models.CharField('Тип', max_length=50)
    area = models.IntegerField('Область измерений', choices=AREAS, default=0)
    document = models.ManyToManyField('Document', blank=True, null=True,
                                      verbose_name='Нормативные документы')
    kt = models.CharField('Погрешность, класс точности', max_length=40, blank=True)
    features = models.TextField('Метрологические характеристики', blank=True)
    interval = models.IntegerField('Межповерочный интервал, мес.', choices=INTERVALS, default=12)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s %s" % (self.name, self.tipo)

    @models.permalink
    def get_absolute_url(self):
        return 'measure_detail', (self.id,)

    class Meta:
        verbose_name = "Тип СИ"
        verbose_name_plural = "Типы СИ"
        unique_together = ('name', 'tipo')
        ordering = ("tipo", "name")


class Document(models.Model):
    code = models.CharField('Код', max_length=50, unique=True)
    name = models.CharField('Название', max_length=255)
    notes = models.TextField('Примечание', blank=True)
    doc = models.FileField('Файл', upload_to='documents/norma', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s. %s" % (self.code, self.name)

    @models.permalink
    def get_absolute_url(self):
        return 'document_detail', (self.id,)

    class Meta:
        ordering = ('code',)
        verbose_name = 'Нормативный документ'
        verbose_name_plural = 'Нормативная документация'


class Image(models.Model):
    measure = models.ForeignKey(Measure, verbose_name='Тип СИ')
    photo = models.ImageField('Файл', upload_to='photos/measures')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"


STATUSES = (
    (0, 'Не определено'), (1, 'В эксплуатации'),
    (2, 'В поверке \\ калибровке \\ аттестации'),
    (3, 'В ремонте'),
    (4, 'Списано'),
    (5, 'Поверен'),
)


class Passport(models.Model):
    measure = models.ForeignKey(Measure, verbose_name='Тип СИ')
    number = models.CharField('Заводской номер', max_length=40)
    organization = models.ForeignKey(Organization, verbose_name='Владелец (организация)')
    department = models.ForeignKey(Department, blank=True, null=True, verbose_name='Владелец (подразделение)')
    interval = models.IntegerField('Межповерочный интервал, мес.')
    manufacturer = models.CharField('Изготовитель', max_length=255, blank=True)
    manufacture_date = models.DateField('Дата изготовления', blank=True, null=True)
    status = models.IntegerField('Текущий статус', choices=STATUSES, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s № %s" % (self.measure.tipo, self.number)

    def owner(self):
        ret = u""
        if self.organization:
            ret += self.organization.name
        if self.organization and self.department:
            ret += ", "
        if self.department:
            ret += self.department.name
        return ret

    def is_debt(self):
        if self.work_set.all().__len__() == 0:
            return False

        latest_date = self.work_set.latest('date').date
        delta = datetime.timedelta(days=self.interval * 30)
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        if latest_date and delta and now:
            if now - delta > latest_date:
                return True

        return False

    def next_date(self):
        if self.work_set.all().__len__() == 0 or self.is_debt():
            return datetime.datetime.now() + datetime.timedelta(days=30)

        latest_date = self.work_set.latest('date').date
        return latest_date + datetime.timedelta(days=30*self.interval)

    @models.permalink
    def get_absolute_url(self):
        return 'passport_detail', (self.id,)

    class Meta:
        unique_together = ('measure', 'number')
        ordering = ("measure", "number")
        verbose_name = 'Средство измерений'
        verbose_name_plural = 'Средства измерений'


class Journal(models.Model):
    passport = models.ForeignKey(Passport, verbose_name='Средство измерений')
    date = models.DateTimeField('Дата', default=datetime.datetime.now)
    passed = models.CharField('Сдал', max_length=255)
    accepted = models.CharField('Принял', max_length=255)
    journal_out = models.OneToOneField('JournalOut', blank=True, null=True,
                                       related_name='journal_out')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"Запись № %s" % self.id

    class Meta:
        verbose_name = "Журнал"
        verbose_name_plural = "Журналы"


class JournalOut(models.Model):
    journal = models.OneToOneField(Journal, related_name='journal')
    date = models.DateTimeField("Дата", default=datetime.datetime.now)
    passed = models.CharField("Выдал", max_length=255)
    accepted = models.CharField("Получил", max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"Запись № %s" % self.id


VERIFICATION_WORK = ((1, 'Поверка'), (3, 'Калибровка'), (4, 'Аттестация'))
REPAIR_WORK = ((2, 'Ремонт'),)


def upload_path(instance, filename):
    return os.path.join('documents/work',
                        instance.date.strftime("%Y"),
                        instance.date.strftime("%m"),
                        filename)


class Work(models.Model):
    passport = models.ForeignKey(Passport, verbose_name='Средство измерений')
    tipo = models.IntegerField('Вид работ', choices=VERIFICATION_WORK + REPAIR_WORK, default=1)
    date = models.DateTimeField('Дата', default=datetime.datetime.now)
    result = models.BooleanField('Результат', default=True)
    performer = models.CharField('Исполнитель', max_length=255)
    workplace = models.CharField('Место работ', max_length=255)
    document = models.FileField('Документ', upload_to=upload_path, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"Работа № %s" % self.id

    def document_name(self):

        if self.result:
            return u"%s_%s" % (self.passport.number, self.passport.measure.tipo)
        else:
            return u"И%s_%s" % (self.passport.number, self.passport.measure.tipo)

    class Meta:
        ordering = ("-date",)
        get_latest_by = "date"
        verbose_name = "Работа"
        verbose_name_plural = "Работы"

