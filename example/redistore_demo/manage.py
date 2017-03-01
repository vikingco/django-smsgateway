#!/usr/bin/env python

from django.core.management import execute_manager
from imp import find_module
from os import environ
from sys import path as sys_path, stderr, exit
import settings  # noqa
sys_path.insert(0, '../..')  # parent of inline_media directory
sys_path.insert(0, '..')

environ['DJANGO_SETTINGS_MODULE'] = 'redistore_demo.settings'

try:
    find_module('settings')  # Assumed to be in the same directory.
except ImportError:
    stderr.write("Error: Can't find the file 'settings.py' in the directory containing {}. It appears you've "
                 "customized things.\nYou'll have to run django-admin.py, passing it your settings"
                 'module.\n'.format(__file__))
    exit(1)

if __name__ == '__main__':
    execute_manager(settings)
