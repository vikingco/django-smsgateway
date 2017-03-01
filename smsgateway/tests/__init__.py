from os import chdir, path, getcwd, environ
from sys import path as sys_path
from unittest import TestSuite, TestLoader


def setup_django_settings():
    chdir(path.join(path.dirname(__file__), '..'))
    sys_path.inser(0, getcwd())
    environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'


def run_tests():
    if not environ.get('DJANGO_SETTINGS_MODULE', False):
        setup_django_settings()

    from django.conf import settings
    from django.test.utils import get_runner

    testrunner = get_runner(settings)
    test_suite = testrunner(verbosity=2, interactive=True, failfast=False)
    test_suite.run_tests(['smsgateway'])


def suite():
    if not environ.get('DJANGO_SETTINGS_MODULE', False):
        setup_django_settings()
    else:
        from django.apps import apps
        from django.conf import settings
        settings.INSTALLED_APPS += ['smsgateway.tests']
        map(apps.load_app, settings.INSTALLED_APPS)

    from smsgateway.tests import tasks
    from smsgateway.tests.backends import smpp, redistore

    testsuite = TestSuite([
        TestLoader().loadTestsFromModule(smpp),
        TestLoader().loadTestsFromModule(redistore),
        TestLoader().loadTestsFromModule(tasks),
    ])
    return testsuite


if __name__ == '__main__':
    run_tests()
