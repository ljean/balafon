#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

VERSION = __import__('sanza').__version__

import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'sanza',
    version = VERSION,
    description = 'Contacts management',
    packages = find_packages(),
    include_package_data = True,
    author = 'Luc Jean',
    author_email = 'ljean@apidev.fr',
    license = 'CeCILL',
    zip_safe = False,
    install_requires = [
        #'coop-cms',
        'django-chosen',
        'beautifulsoup4',
        'BeautifulSoup',
        'django-wkhtmltopdf',
        'django-form-utils',
        'xlwt==0.7.5',
        'xlrd',
        'django-simple-captcha',
    ],
    long_description = open('README.rst').read(),
    url = 'https://bitbucket.org/ljean/apidev-sanza',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Natural Language :: English',
        'Natural Language :: French',
        'Topic :: Office/Business',
    ],
)

