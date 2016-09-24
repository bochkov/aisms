# coding=utf-8
import datetime
from django.db import models, connection
from django.contrib import admin


class Position(models.Model):
    position = models.CharField("Должность",
                                max_length=100,
                                unique=True)

    def __unicode__(self):
        return self.position

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"


class PositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'position')


class Organization(models.Model):
    name = models.CharField("Название",
                            max_length=255,
                            unique=True)
    short_name = models.CharField("Краткое название",
                                  max_length=100,
                                  blank=True,
                                  null=True)
    inn = models.CharField("ИНН",
                           max_length=10,
                           blank=True,
                           null=True)
    kpp = models.CharField("КПП",
                           max_length=10,
                           blank=True,
                           null=True)
    ogrn = models.CharField("ОГРН",
                            max_length=10,
                            blank=True,
                            null=True)
    u_address = models.CharField("Юр. адрес",
                                 max_length=255,
                                 blank=True,
                                 null=True)
    f_address = models.CharField("Физ. адрес",
                                 max_length=255,
                                 blank=True,
                                 null=True)
    p_address = models.CharField("Почт. адрес",
                                 max_length=255,
                                 blank=True,
                                 null=True)
    okved = models.CharField("ОКВЭД",
                             max_length=10,
                             blank=True,
                             null=True)
    okato = models.CharField("ОКАТО",
                             max_length=10,
                             blank=True,
                             null=True)
    okpo = models.CharField("ОКПО",
                            max_length=10,
                            blank=True,
                            null=True)
    bank = models.CharField("Банк",
                            max_length=100,
                            blank=True,
                            null=True)
    bik = models.CharField("БИК",
                           max_length=10,
                           blank=True,
                           null=True)
    cor_account = models.CharField("Корр. счет",
                                   max_length=20,
                                   blank=True,
                                   null=True)
    cur_account = models.CharField("Расч. счет",
                                   max_length=20,
                                   blank=True,
                                   null=True)
    director = models.CharField("Руководитель",
                                max_length=40,
                                blank=True,
                                null=True)
    position = models.CharField("Должность руководителя",
                                max_length=40,
                                blank=True,
                                null=True)

    def __unicode__(self):
        return self.name if self.short_name == "" else self.short_name

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"
        ordering = ('name',)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'short_name', 'director')
    fieldsets = [
        (None, {
            "fields": ['name', 'short_name', 'director', 'position']}),
        ("Реквизиты", {
            "fields": ['inn', 'kpp', 'ogrn', 'bank', 'bik', 'cor_account', 'cur_account'],
            "classes": ['collapse']}),
        ("Адреса", {
            'fields': ['u_address', 'f_address', 'p_address'],
            "classes": ['collapse']}),
        ("Другое", {
            'fields': ['okved', 'okato', 'okpo'],
            "classes": ['collapse']}),
    ]


class Department(models.Model):
    organization = models.ForeignKey(Organization,
                                     verbose_name="Организация")
    code = models.CharField("Код позразделения",
                            max_length=15,
                            unique=True)
    name = models.CharField("Название",
                            max_length=255)
    short_name = models.CharField("Краткое название",
                                  max_length=20,
                                  blank=True,
                                  null=True)

    def __unicode__(self):
        return self.code if self.short_name == "" \
            else u"{0} {1}".format(self.code, self.short_name)

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"
        ordering = ('code',)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'short_name', 'name')


class People(models.Model):
    tab_num = models.CharField("Табельный номер",
                               max_length=10,
                               blank=True,
                               null=True)
    last_name = models.CharField("Фамилия",
                                 max_length=30)
    first_name = models.CharField("Имя",
                                  max_length=20)
    middle_name = models.CharField("Отчество",
                                   max_length=40,
                                   blank=True,
                                   null=True)
    phone = models.CharField("Телефон",
                             max_length=10,
                             blank=True,
                             null=True)
    position = models.ForeignKey(Position,
                                 verbose_name="Должность")
    department = models.ForeignKey(Department,
                                   verbose_name="Подразделение")

    def __unicode__(self):
        if self.middle_name == "":
            return u"{0} {1}.".format(self.last_name, self.first_name[:1])

        return u"{0} {1}.{2}.".format(self.last_name, self.first_name[:1], self.middle_name[:1])

    class Meta:
        unique_together = ('last_name', 'first_name', 'middle_name')
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class PeopleAdmin(admin.ModelAdmin):
    list_display = ('tab_num', '__unicode__', 'department')


class Area(models.Model):
    AREA_CHOICE = [
        (27, 'Геометрические'),
        (28, 'Механические'),
        (29, 'Расхода, вместимости, уровня, параметров потока'),
        (30, 'Давления и вакуума'),
        (31, 'Физико-химические'),
        (32, 'Температурные и теплофизические'),
        (33, 'Времени и частоты'),
        (34, 'Электрические и магнитные'),
        (35, 'Радиоэлектронные'),
        (36, 'Виброакустические'),
        (37, 'Оптические и оптико-физические'),
        (38, 'Ионизирующие излучения и ядерныx констант'),
        (39, 'Биологические и биомедицинские'),
    ]
    area = models.IntegerField("Область измерений",
                               unique=True, choices=AREA_CHOICE)

    def __unicode__(self):
        return self.get_area_display()

    class Meta:
        verbose_name = "Область измерения"
        verbose_name_plural = "Области измерений"
        ordering = ('area',)


class AreaAdmin(admin.ModelAdmin):
    list_display = ('area',)


class Status(models.Model):
    STATUS_CHOICE = [
        (0, 'Не определено'),
        (1, 'Эксплуатация'),
        (2, 'Поверка'),
        (3, 'Ремонт'),
        (4, 'Хранение'),
        (5, 'Списано'),
    ]
    status = models.IntegerField("Статус",
                                 unique=True,
                                 choices=STATUS_CHOICE)

    def __unicode__(self):
        return self.get_status_display()

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ('status',)


class StatusAdmin(admin.ModelAdmin):
    list_display = ('status',)


class Document(models.Model):
    code = models.CharField("Обозначение",
                            max_length=100,
                            unique=True)
    name = models.CharField("Название",
                            max_length=255)

    def __unicode__(self):
        return self.code

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ('code',)


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


class Measure(models.Model):
    INTERVAL_CHOICE = [
        (6, '6'),
        (12, '12'),
        (18, '18'),
        (24, '24'),
        (36, '36'),
        (48, '48'),
    ]
    name = models.CharField("Наименование",
                            max_length=255)
    type = models.CharField("Тип",
                            max_length=20)
    area = models.ForeignKey(Area,
                             verbose_name="Область измерений")
    features = models.TextField("Характеристики",
                                blank=True,
                                null=True)
    interval = models.IntegerField("Межповерочный интервал",
                                   choices=INTERVAL_CHOICE)
    image = models.ImageField("Изображение",
                              upload_to='photos',
                              blank=True,
                              null=True)
    documents = models.ManyToManyField(Document,
                                       blank=True,
                                       null=True,
                                       verbose_name="Нормативные документы")

    def __unicode__(self):
        return u"{0} {1}".format(self.name, self.type)

    class Meta:
        unique_together = ('name', 'type')
        verbose_name = "Средство измерений"
        verbose_name_plural = "Средства измерений"
        ordering = ('area', 'name', 'type')


class MeasureAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'area', 'interval')
    search_fields = ('name', 'type')


def by_years():
    cursor = connection.cursor()
    # т.к. status_id = status + 1
    query = "SELECT year, count(id) FROM aisms_passport " \
            "WHERE status_id <> 6 GROUP BY year"
    cursor.execute(query)

    result_list = []
    for row in cursor.fetchall():
        result_list.append((row[0], row[1]))
    return result_list


class PassportManager(models.Manager):
    def plan(self, organization):
        if organization is None:
            return []

        cursor = connection.cursor()
        query = "SELECT DISTINCT p.number, d.code, d.short_name, " \
                "m.name, m.type, m.interval, s.status, w_date, a.area " \
                "FROM aisms_passport AS p " \
                "INNER JOIN aisms_status AS s ON p.status_id = s.status " \
                "INNER JOIN aisms_measure AS m ON m.id = p.measure_id " \
                "INNER JOIN aisms_department AS d ON d.id = department_id " \
                "INNER JOIN aisms_organization AS o ON o.id = d.organization_id " \
                "INNER JOIN aisms_area AS a ON m.area_id = a.id " \
                "LEFT JOIN ( " \
                "SELECT w.passport_id AS passport_id, w.date AS w_date, org.id AS org " \
                "FROM aisms_work AS w " \
                "INNER JOIN aisms_worktype AS wt ON w.worktype_id = wt.id " \
                "INNER JOIN aisms_organization AS org ON org.id = w.organization_id " \
                "WHERE w.result == 1 AND wt.worktype <> 5 " \
                "ORDER BY w.date DESC) " \
                "ON passport_id = p.id " \
                "WHERE (s.status <> 4 OR s.status <> 5) AND (org = '{0}' OR org = '') " \
                "ORDER BY m.area_id, m.name, m.type, p.number".format(organization)
        cursor.execute(query)

        result_list = []
        for row in cursor.fetchall():
            p = self.model(number=row[0])
            p.department = Department(code=row[1], short_name=row[2])
            p.measure = Measure(name=row[3], type=row[4], interval=row[5],
                                area=Area(area=row[8]))
            p.status = Status(status=row[6] - 1)
            p.date = row[7]
            if p.date:
                p.next_date = p.date + datetime.timedelta(days=30 * row[5])
            result_list.append(p)
        return result_list

    @staticmethod
    def by_deps():
        cursor = connection.cursor()
        query = "SELECT d.name, count(p.id) " \
                "FROM aisms_passport AS p " \
                "INNER JOIN aisms_department AS d ON d.id=p.department_id " \
                "WHERE status_id <> 6 " \
                "GROUP BY p.department_id"
        cursor.execute(query)

        result_list = []
        for row in cursor.fetchall():
            result_list.append((row[0], row[1]))
        return result_list


class Passport(models.Model):
    measure = models.ForeignKey(Measure,
                                verbose_name="Средство измерений")
    number = models.CharField("Зав.номер",
                              max_length=20)
    department = models.ForeignKey(Department,
                                   verbose_name="Подразделение")
    year = models.CharField("Год выпуска",
                            max_length=4,
                            blank=True,
                            null=True)
    manufacturer = models.CharField("Изготовитель",
                                    max_length=100,
                                    blank=True,
                                    null=True)
    status = models.ForeignKey(Status,
                               verbose_name="Текущее состояние")

    objects = PassportManager()

    def __unicode__(self):
        return u"{0} №{1}".format(self.measure.type, self.number)

    class Meta:
        verbose_name = "Паспорт"
        verbose_name_plural = "Паспорты"
        unique_together = ('measure', 'number')


class PassportAdmin(admin.ModelAdmin):
    list_display = ('measure', 'number', 'year', 'manufacturer')
    list_filter = ('department', 'status')
    search_fields = ('measure', 'number')


class Worktype(models.Model):
    WORK_CHOICES = [
        (0, 'Не определено'),
        (1, 'Поверка'),
        (2, 'Калибровка'),
        (3, 'Проверка'),
        (4, 'Аттестация'),
        (5, 'Ремонт'),
    ]
    worktype = models.IntegerField("Вид работ",
                                   unique=True,
                                   choices=WORK_CHOICES)

    def __unicode__(self):
        return self.get_worktype_display()

    class Meta:
        verbose_name = "Вид работ"
        verbose_name_plural = "Виды работ"
        ordering = ('worktype',)


class WorktypeAdmin(admin.ModelAdmin):
    list_display = ('worktype',)


class Work(models.Model):
    passport = models.ForeignKey(Passport,
                                 verbose_name="Паспорт")
    worktype = models.ForeignKey(Worktype,
                                 verbose_name="Вид работ")
    date = models.DateTimeField("Дата работ")
    organization = models.ForeignKey(Organization,
                                     verbose_name="Организация")
    performer = models.CharField("Исполнитель",
                                 max_length=100)
    result = models.BooleanField("Годен")

    def __unicode__(self):
        return u"{0} {1}".format(self.worktype, self.passport)

    class Meta:
        verbose_name = "Работа"
        verbose_name_plural = "Работы"


class WorkAdmin(admin.ModelAdmin):
    list_display = ('passport', 'date', 'result')
    list_filter = ('worktype', 'organization')


class Verificator(models.Model):
    people = models.ForeignKey(People,
                               verbose_name="Люди")
    area = models.ManyToManyField(Area,
                                  through='AttestationDate')

    def __unicode__(self):
        return self.people.__unicode__()

    class Meta:
        verbose_name = "Поверитель"
        verbose_name_plural = "Поверители"


class AttestationDate(models.Model):
    verificator = models.ForeignKey(Verificator,
                                    verbose_name="Поверитель")
    area = models.ForeignKey(Area,
                             verbose_name="Область измерений")
    att_date = models.DateField("Дата аттестации")

    class Meta:
        ordering = ('att_date',)
        verbose_name = "Дата аттестации"
        verbose_name_plural = "Даты аттестации"


class AttestationInline(admin.TabularInline):
    model = AttestationDate
    extra = 1


class VerificatorAdmin(admin.ModelAdmin):
    list_display = ('people',)
    inlines = [AttestationInline]


class Repairmen(models.Model):
    people = models.ForeignKey(People, verbose_name='Люди')

    def __unicode__(self):
        return self.people.__unicode__()

    class Meta:
        verbose_name = "Ремонтник"
        verbose_name_plural = "Ремонтники"


class RepairmenAdmin(admin.ModelAdmin):
    list_display = ('people',)


class JournalReception(models.Model):
    passport = models.ForeignKey(Passport,
                                 verbose_name='Паспорт')
    in_date = models.DateTimeField("Дата приемки")
    in_pass = models.CharField("Сдал",
                               max_length=100)
    in_took = models.CharField("Принял",
                               max_length=100)
    out_date = models.DateTimeField("Дата выдачи",
                                    null=True,
                                    blank=True)
    out_pass = models.CharField("Выдал",
                                max_length=100,
                                blank=True,
                                null=True)
    out_took = models.CharField("Получил",
                                max_length=100,
                                blank=True,
                                null=True)
    notes = models.CharField("Примечание",
                             max_length=255,
                             null=True,
                             blank=True)
    is_active = models.BooleanField("Активно",
                                    default=True)
    is_done = models.BooleanField("Можно выдавать?",
                                  default=False)

    def __unicode__(self):
        return u"Запись № {0}".format(self.id)

    class Meta:
        verbose_name = "Запись в журнале"
        verbose_name_plural = "Журнал приемки"
        ordering = ('-in_date',)


class JournalReceptionAdmin(admin.ModelAdmin):
    list_display = ('passport', 'in_date', 'in_pass', 'in_took',
                    'out_date', 'out_pass', 'out_took', 'notes')
    list_filter = ('is_active', 'is_done')


class JournalVerificationManager(models.Manager):
    def report(self, from_date, to_date, name):
        result = super(JournalVerificationManager, self).get_query_set().filter(
            out_date__range=(from_date, to_date)).order_by('out_date')
        if not name == '':
            result = result.filter(verificator=name)
        return result


class JournalVerification(models.Model):
    passport = models.ForeignKey(Passport,
                                 verbose_name='Паспорт')
    in_date = models.DateTimeField("Дата поступления")
    verificator = models.CharField("Поверитель",
                                   max_length=255,
                                   blank=True,
                                   null=True)
    result = models.NullBooleanField("Результат",
                                     default=None)
    out_date = models.DateTimeField("Дата выдачи",
                                    blank=True,
                                    null=True)
    notes = models.CharField("Примечание",
                             max_length=255,
                             blank=True,
                             null=True)
    is_active = models.BooleanField("Активно",
                                    default=True)

    objects = JournalVerificationManager()

    def __unicode__(self):
        return u"Запись № {0}".format(self.id)

    class Meta:
        verbose_name = "Запись в журнале"
        verbose_name_plural = "Журнал поверок"
        ordering = ('-out_date',)


class JournalVerificationAdmin(admin.ModelAdmin):
    list_display = ('passport', 'in_date', 'verificator',
                    'result', 'out_date', 'notes')
    list_filter = ('is_active',)


class JournalRepairManager(models.Manager):
    def report(self, from_date, in_date, name):
        from django.db import connection

        cursor = connection.cursor()
        query = "SELECT j.id, m.name, m.type, p.number, d.code, j.result, j.out_date, j.notes " \
                "FROM aisms_journalrepair as j " \
                "INNER JOIN aisms_passport AS p ON j.passport_id = p.id " \
                "INNER JOIN aisms_measure AS m ON p.measure_id = m.id " \
                "INNER JOIN aisms_department AS d ON p.department_id = d.id " \
                "WHERE j.out_date BETWEEN '{0}' AND '{1}'".format(from_date, in_date)
        if not name == '':
            query += " AND repairmen = '{0}'".format(name)
        cursor.execute(query)
        result_list = []
        for row in cursor.fetchall():
            p = self.model(id=row[0], result=row[5], out_date=row[6],
                           notes="" if row[7] else row[7])  # row[6] = True if null
            p.measure = u"{0} {1}".format(row[1], row[2])
            p.number = row[3]
            p.department = row[4]
            result_list.append(p)
        return result_list


class JournalRepair(models.Model):
    passport = models.ForeignKey(Passport,
                                 verbose_name='Паспорт')
    in_date = models.DateTimeField("Дата поступления")
    reason = models.CharField("Причина",
                              max_length=255)
    repairmen = models.CharField("Ремонтник",
                                 max_length=100,
                                 blank=True,
                                 null=True)
    out_date = models.DateTimeField("Дата ремонта",
                                    blank=True,
                                    null=True)
    result = models.NullBooleanField("Результат",
                                     default=None)
    notes = models.CharField("Примечание",
                             max_length=255,
                             blank=True,
                             null=True)
    is_active = models.BooleanField("Активно",
                                    default=True)

    objects = JournalRepairManager()

    def __unicode__(self):
        return u"Запись № {0}".format(self.id)

    class Meta:
        verbose_name = "Запись в журнале"
        verbose_name_plural = "Журнал ремонта"
        ordering = ('-in_date',)


class JournalRepairAdmin(admin.ModelAdmin):
    list_display = ('passport', 'in_date', 'reason',
                    'repairmen', 'out_date', 'result', 'notes')
    list_filter = ('is_active',)


admin.site.register(Position, PositionAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(People, PeopleAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Measure, MeasureAdmin)
admin.site.register(Passport, PassportAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Worktype, WorktypeAdmin)
admin.site.register(Work, WorkAdmin)
admin.site.register(Verificator, VerificatorAdmin)
admin.site.register(Repairmen, RepairmenAdmin)
admin.site.register(JournalReception, JournalReceptionAdmin)
admin.site.register(JournalVerification, JournalVerificationAdmin)
admin.site.register(JournalRepair, JournalRepairAdmin)
