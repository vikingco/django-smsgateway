from setuptools import setup, find_packages
import smsgateway


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
)
