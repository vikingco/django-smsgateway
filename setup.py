from setuptools import setup, find_packages
from setuptools.command.test import test
import smsgateway
import subprocess
import os


def run_tests(*args):
    SMPPSIM_DIR = os.path.join(os.path.abspath(os.path.curdir),
                               'tests/SMPPSim')
    print "Launch SMPPSim service for testing... ",
    subprocess.Popen(['/bin/sh', os.path.join(SMPPSIM_DIR, 'do_start.sh')],
                     stdout=open('/dev/null', 'w'), 
                     stderr=subprocess.STDOUT,
                     cwd=SMPPSIM_DIR).wait()
    if os.path.exists(os.path.join(SMPPSIM_DIR, 'service.pid')):
        print 'Ok'
    else: print 'failed!'
    subprocess.Popen(['python', 'tests/runtests.py']).wait()
    print "Stopping SMPPSim service... ",
    subprocess.Popen(['/bin/sh', os.path.join(SMPPSIM_DIR, 'do_stop.sh')],
                     cwd=SMPPSIM_DIR).wait()
    if os.path.exists(os.path.join(SMPPSIM_DIR, 'service.pid')):
        print 'failed!'
    else: print 'Ok'
test.run_tests = run_tests


setup(
    name="django-smsgateway",
    version=smsgateway.__version__,
    url='https://github.com/citylive/django-smsgateway',
    license='BSD',
    description="SMS gateway for sending text messages",
    long_description=open('README.rst', 'r').read(),
    author='Jef Geskens, City Live nv',
    packages=find_packages('.'),
    package_data={'smsgateway': [
                'templates/*.html', 'templates/*/*.html', 'templates/*/*/*.html',
                'locale/*/LC_MESSAGES/*.mo', 'locale/*/LC_MESSAGES/*.po',
                ], },
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
    test_suite = 'dummy'
)
