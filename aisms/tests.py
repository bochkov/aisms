# coding: utf-8
import datetime
from django import test
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import pytz
from aisms import models


def login(func):
    def wrap(self):
        is_logged_in = self.c.login(username='test', password='test')
        self.assertTrue(is_logged_in)
        return func(self)
    return wrap


def template_and_status(tmpl=None, status=200):
    def decorator(func):
        def wrap(self):
            response = func(self)
            if tmpl is not None:
                tmplist = tmpl.split(",")
                for i in tmplist:
                    self.assertTemplateUsed(response, i.strip())
            self.assertEqual(response.status_code, status)
        return wrap
    return decorator


## Models Test ###


class MyTestCase(test.TestCase):
    fixtures = ('organization.json', 'department.json',
                'measure.json', 'document.json', 'image.json',
                'passport.json')

    def setUp(self):
        self.c = test.client.Client()
        self.user = User.objects.create_user(username="test", email="test@test.com", password="test")


class IndexTest(MyTestCase):
    @template_and_status('index.html')
    def test_index(self):
        return self.c.get(reverse('index'))


class OrganizationTest(MyTestCase):

    @login
    @template_and_status('models/organization/list.html')
    def test_login_list(self):
        return self.c.get(reverse('organization_list'))

    @template_and_status(status=302)
    def test_list(self):
        return self.c.get(reverse('organization_list'))

    @login
    @template_and_status('models/organization/add.html')
    def test_login_create(self):
        return self.c.get(reverse('add_organization'))

    @template_and_status(status=302)
    def test_create(self):
        return self.c.get(reverse('add_organization'))

    @login
    @template_and_status('models/organization/add.html')
    def test_invalid_create(self):
        data = {'full_name': 'Test'}
        response = self.c.post(reverse('add_organization'), data)
        self.assertFormError(response, 'form', 'name', u'Обязательное поле.')
        return response

    @login
    @template_and_status(status=302)
    def test_valid_create(self):
        data = {'name': 'Test'}
        return self.c.post(reverse('add_organization'), data)

    @login
    def test_not_unique(self):
        data = {'name': 'Test'}
        self.c.post(reverse('add_organization'), data)
        response = self.c.post(reverse('add_organization'), data)
        self.assertFormError(response, 'form', 'name', u'Организация с таким Наименование уже существует.')

    @login
    @template_and_status('models/organization/detail.html')
    def test_login_detail(self):
        return self.c.get(reverse('organization_detail', args=[5]))

    @template_and_status(status=302)
    def test_detail(self):
        return self.c.get(reverse("organization_detail", args=[5]))

    @login
    def test_unicode(self):
        r = self.c.get(reverse('organization_detail', args=[1]))
        self.assertEqual(r.context['object'].__unicode__(), u'1: ОАО "ПО "УОМЗ" им. Э.С. Яламова"')


class DepartmentTest(MyTestCase):

    @login
    @template_and_status('models/department/list.html')
    def test_login_list(self):
        return self.c.get(reverse('department_list'))

    @template_and_status(status=302)
    def test_list(self):
        return self.c.get(reverse('department_list'))

    @login
    @template_and_status('models/department/detail.html')
    def test_login_detail(self):
        return self.c.get(reverse('department_detail', args=[3]))

    @template_and_status(status=302)
    def test_detail(self):
        return self.c.get(reverse('department_detail', args=[3]))

    @login
    def test_unicode(self):
        r = self.c.get(reverse('department_detail', args=[3]))
        self.assertEqual(r.context['object'].__unicode__(), u'Отдел главного метролога')

    @login
    @template_and_status('models/department/add.html')
    def test_create(self):
        return self.c.get(reverse('add_department'))

    @template_and_status(status=302)
    def test_login_create(self):
        return self.c.get(reverse('add_department'))

    @login
    def test_not_unique(self):
        data = {'name': 'Test', 'organization': 1}
        self.c.post(reverse('add_department'), data)
        r = self.c.post(reverse('add_department'), data)
        self.assertFormError(r, 'form', None, u'Подразделение с таким Название и Организация уже существует.')

    @login
    @template_and_status('models/department/add.html')
    def test_invalid_create(self):
        r = self.c.post(reverse('add_department'), {'name': 'Test'})
        self.assertFormError(r, 'form', 'organization', u'Обязательное поле.')
        r = self.c.post(reverse('add_department'), {'organization': 2})
        self.assertFormError(r, 'form', 'name', u'Обязательное поле.')
        return r

    @login
    @template_and_status(status=302)
    def test_valid_create(self):
        data = {'name': 'Test', 'organization': 1}
        return self.c.post(reverse('add_department'), data)


class MeasureTest(MyTestCase):

    @template_and_status('models/measure/list.html')
    def test_list(self):
        return self.c.get(reverse('measure_list'))

    @template_and_status('models/measure/detail.html')
    def test_detail(self):
        return self.c.get(reverse('measure_detail', args=[3]))

    @login
    def test_add_not_unique(self):
        data = {
            "name": "Test", "tipo": "Test", "area": 0, "kt": "",
            "features": "", "interval": "12"
        }
        self.c.post(reverse('add_measure'), data)
        r = self.c.post(reverse('add_measure'), data)
        self.assertFormError(r, 'form', None, u'Тип СИ с таким Наименование и Тип уже существует.')

    @template_and_status(status=302)
    def test_notlogin_create(self):
        return self.c.get(reverse('add_measure'))

    @login
    @template_and_status(status=302)
    def test_valid_create(self):
        data = {
            "name": "Test", "tipo": "Test", "area": 0, "kt": "",
            "features": "", "interval": "12"
        }
        return self.c.post(reverse('add_measure'), data)

    @login
    def test_invalid_create(self):
        r = self.c.post(reverse('add_measure'), {"name": "Test"})
        self.assertFormError(r, 'form', 'tipo', u'Обязательное поле.')
        r = self.c.post(reverse('add_measure'), {"type": "Test"})
        self.assertFormError(r, 'form', "name", u'Обязательное поле.')


class DocumentTest(MyTestCase):

    @template_and_status('models/document/list.html')
    def test_list(self):
        return self.c.get(reverse('document_list'))

    @template_and_status('models/document/detail.html')
    def test_detail(self):
        return self.c.get(reverse('document_detail', args=[2]))

    # TODO
    def test_file(self):
        pass

    @login
    @template_and_status('models/document/add.html')
    def test_add_not_unique(self):
        data = {'code': 'Test', 'name': 'Test'}
        self.c.post(reverse('add_document'), data)
        r = self.c.post(reverse('add_document'), data)
        self.assertFormError(r, 'form', 'code', u'Нормативный документ с таким Код уже существует.')
        return r

    def test_notlogin_create(self):
        r = self.c.get(reverse('add_document'))
        self.assertEqual(r.status_code, 302)
        r = self.c.post(reverse('add_document'), {'code': 'Test', 'name': 'Test'})
        self.assertEqual(r.status_code, 302)

    @login
    @template_and_status(status=302)
    def test_valid_create(self):
        return self.c.post(reverse('add_document'), {'code': 'Test', 'name': 'Test'})

    @login
    def invalid_create(self):
        r = self.c.post(reverse('add_document'), {'code': 'Test'})
        self.assertFormError(r, 'form', 'name', u'Обязательное поле.')
        r = self.c.post(reverse('add_document'), {'name': 'Test'})
        self.assertFormError(r, 'form', 'code', u'Обязательное поле.')


# TODO
class ImageTest(MyTestCase):
    pass


class PassportTest(MyTestCase):
    @template_and_status('models/passport/detail.html')
    def test_detail(self):
        r = self.c.get(reverse('passport_detail', args=[3]))
        self.assertTrue('object' in r.context)
        return r

    @template_and_status('models/passport/list.html')
    def test_list(self):
        r = self.c.get(reverse('passport_list'))
        self.assertTrue('object_list' in r.context)
        return r

    def test_owner(self):
        p = models.Passport.objects.get(pk=1)
        org = p.organization.name
        dep = p.department.name
        self.assertEqual(p.owner(), "%s, %s" % (org, dep))

        p = models.Passport.objects.get(pk=3)
        org = p.organization.name
        self.assertEqual(p.owner(), "%s" % org)

    @template_and_status(status=302)
    def test_notlogin_create(self):
        data = {'measure': 1, 'number': 13, 'organization': 1, 'interval': 12}
        return self.c.post(reverse('add_passport'), data)

    @login
    def test_invalid_create(self):
        data = {'measure': 1}
        r = self.c.post(reverse('add_passport'), data)
        self.assertFormError(r, 'form', 'number', u'Обязательное поле.')
        self.assertFormError(r, 'form', 'organization', u'Обязательное поле.')
        self.assertFormError(r, 'form', 'interval', u'Обязательное поле.')

    @login
    @template_and_status('models/passport/add.html')
    def test_valid_create(self):
        data = {'measure': 1, 'number': 13, 'organization': 1, 'interval': 12}
        return self.c.post(reverse('add_passport'), data)

    @login
    def test_debt(self):
        p = models.Passport.objects.create(
            measure=models.Measure.objects.get(pk=2),
            number='124',
            organization=models.Organization.objects.get(pk=4),
            interval=6)
        self.assertFalse(p.is_debt())
        tz = pytz.UTC
        models.Work.objects.create(passport=p, date=datetime.datetime(2009, 5, 12, 9, 0, 0, tzinfo=tz))
        self.assertTrue(p.is_debt())

    @login
    def test_next_date(self):
        p = models.Passport.objects.get(pk=8)
        w = models.Work.objects.create(passport=p, date=datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
        self.assertEqual(p.next_date(), w.date + datetime.timedelta(days=30*p.interval))

        p = models.Passport.objects.get(pk=9)
        date1 = p.next_date().replace(microsecond=0)
        date2 = (datetime.datetime.now() + datetime.timedelta(days=30)).replace(microsecond=0)
        self.assertEqual(date1, date2)


class WorkTest(MyTestCase):
    @template_and_status(status=302)
    def test_notlogin_reception(self):
        return self.c.post(reverse('work_reception'), {})

    @template_and_status(status=302)
    def test_notlogin_verification_list(self):
        return self.c.get(reverse('work_verification_list'))

    @template_and_status(status=302)
    def test_notlogin_repair_list(self):
        return self.c.get(reverse('work_repair_list'))

    @login
    @template_and_status(status=302)
    def test_reception(self):
        data = {'passport': 1, 'passed': u'Иванов', 'accepted': u'Петров',
                'date': datetime.datetime.utcnow().strftime("%d.%m.%Y")}
        r = self.c.post(reverse('work_reception'), data)
        self.assertEqual(models.Passport.objects.get(pk=1).status, 2)
        return r

    @login
    @template_and_status('work/verification_list.html, work/_work.html, _base.html')
    def test_verification_list(self):
        r = self.c.get(reverse('work_verification_list'))
        self.assertTrue('object_list' in r.context)
        return r

    @login
    @template_and_status('work/repair_list.html')
    def test_repair_list(self):
        r = self.c.get(reverse('work_repair_list'))
        self.assertTrue('object_list' in r.context)
        return r

    @login
    @template_and_status('work/issue_list.html')
    def test_issue_list(self):
        r = self.c.get(reverse('work_issue_list'))
        self.assertTrue('object_list' in r.context)
        return r

    # TODO
    def test_issue(self):
        pass


class ViewsTest(MyTestCase):
    @login
    @template_and_status('report/works_type.html')
    def test_report_works_type(self):
        r = self.c.get(reverse('report_works_type'))
        self.assertTrue('object_list' in r.context)
        self.assertTrue('type' in r.context)
        return r

    @login
    @template_and_status('report/works_performer.html')
    def test_report_works_performer(self):
        r = self.c.get(reverse('report_works_performer'), {
            'performer': 1, 'from_date': "10.11.2012", 'to_date': "10.11.2011"})
        self.assertFormError(r, 'form', None, u'First time cannot be greather than second time')
        r = self.c.post(reverse('report_works_performer'), {'performer': 1})
        self.assertTrue('object_list' in r.context)
        return r

    @login
    @template_and_status('report/journal.html')
    def test_report_journal(self):
        r = self.c.get(reverse('report_journal'))
        self.assertTrue('object_list' in r.context)
        self.assertTrue('type' in r.context)
        return r

    @template_and_status('report/done.html')
    def test_report_done(self):
        return self.c.get(reverse('report_done'))

    @template_and_status('report/debt.html')
    def test_report_debt(self):
        return self.c.get(reverse('report_debt'))

    @login
    @template_and_status('report/plan.html')
    def test_report_plan(self):
        return self.c.get(reverse('report_plan'))

    @login
    @template_and_status('report/plan_detail.html')
    def test_report_plan_detail(self):
        r = self.c.get(reverse('report_plan_detail', args=[3]))
        self.assertTrue('object_list' in r.context)
        self.assertTrue('organization' in r.context)
        return r

    @login
    @template_and_status()
    def test_print_plan(self):
        return self.c.get(reverse('print_plan', args=[6]))

    def test_interval_by_type(self):
        r = self.c.get('/interval_by_type/', {'measure_id': 1})
        self.assertEqual(r._headers['content-type'][1], 'application/json')
        self.assertTrue("interval" in r.serialize())

    def test_number_search(self):
        r = self.c.post(reverse('number_search'), {'number': '124'})
        self.assertTrue('object_list' in r.context)


# TODO
class VerificationDocumentViewTest(MyTestCase):
    pass