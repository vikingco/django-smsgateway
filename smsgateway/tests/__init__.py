import os
import sys
import unittest


def setup_django_settings():
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.inser(0, os.getcwd())
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'


def run_tests():
    if not os.environ.get('DJANGO_SETTINGS_MODULE', False):
        setup_django_settings()

    from django.conf import settings
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_suite = TestRunner(verbosity=2, interactive=True, failfast=False)
    test_suite.run_tests(['smsgateway'])


def suite():
    if not os.environ.get('DJANGO_SETTINGS_MODULE', False):
        setup_django_settings()
    else:
        from django.apps import apps
        from django.conf import settings
        settings.INSTALLED_APPS += ['smsgateway.tests',]
        map(apps.load_app, settings.INSTALLED_APPS)

    from smsgateway.tests import tasks
    from smsgateway.tests.backends import smpp, redistore

    testsuite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromModule(smpp),
        unittest.TestLoader().loadTestsFromModule(redistore),
        unittest.TestLoader().loadTestsFromModule(tasks),
    ])
    return testsuite

if __name__ == '__main__':
    run_tests()
