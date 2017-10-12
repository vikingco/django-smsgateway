from setuptools import setup, find_packages
from pip.req import parse_requirements
from pip.download import PipSession

from os import path
from smsgateway import __version__


# Lists of requirements and dependency links which are needed during runtime, testing and setup
install_requires = []
tests_require = []
dependency_links = []

# Inject test requirements from requirements_test.txt into setup.py
requirements_file = parse_requirements(path.join('requirements', 'requirements.txt'), session=PipSession())
for req in requirements_file:
    install_requires.append(str(req.req))
    if req.link:
        dependency_links.append(str(req.link))

# Inject test requirements from requirements_test.txt into setup.py
requirements_test_file = parse_requirements(path.join('.', 'requirements', 'requirements_test.txt'), session=PipSession())
for req in requirements_test_file:
    tests_require.append(str(req.req))
    if req.link:
        dependency_links.append(str(req.link))


setup(
    name='django-smsgateway',
    version=__version__,
    url='https://github.com/vikingco/smsgateway',
    license='BSD',
    description='SMS gateway for sending text messages',
    long_description=open('README.rst', 'r').read(),
    author='Unleashed NV',
    author_email='operations@unleashed.be',
    packages=find_packages('.'),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    setup_requires=['pytest-runner', ],
    tests_require=tests_require,
    dependency_links=dependency_links,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
)
