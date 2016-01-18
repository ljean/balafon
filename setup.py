#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

VERSION = __import__('sanza').__version__

setup(
    name='apidev-sanza',
    version=VERSION,
    description='Contacts management',
    packages=find_packages(),
    include_package_data=True,
    author='Luc Jean',
    author_email='ljean@apidev.fr',
    license='CeCILL 2.1',
    zip_safe=False,
    install_requires=[
        'django', # road to 1.9
        'djangorestframework',
        'apidev-coop_cms',
        'beautifulsoup4',
        'BeautifulSoup',
        'django-wkhtmltopdf',
        'xlwt',
        'xlrd',
        'django-simple-captcha',
        'django-registration',
        'model_mommy',
        'django-tastypie',
        'django-cors-headers',
    ],
    dependency_links=[
        'git+https://github.com/ljean/coop_cms.git@dfed5fb535ff4986177f37b42f1d3e2568015a7a#egg=apidev_coop_cms-dev',
    ],
    long_description=open('README.rst').read(),
    url='https://bitbucket.org/ljean/apidev-sanza',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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

