#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

VERSION = __import__('balafon').__version__

setup(
    name='balafon',
    version=VERSION,
    description='Contacts management',
    packages=find_packages(),
    include_package_data=True,
    author='Luc Jean',
    author_email='ljean@apidev.fr',
    license='CeCILL 2.1',
    zip_safe=False,
    install_requires=[
        'django >= 1.9, <1.11',
        'djangorestframework==3.4.7',
        'django-extensions==1.7.5',
        'apidev-coop_cms >= 1.2',
        'beautifulsoup4',
        'django-wkhtmltopdf',
        'xlwt',
        'xlrd',
        'django-simple-captcha',
        'django-registration',
        'model_mommy',
        'django-tastypie',
        'django-cors-headers',
    ],
    dependency_links = [
        # Python3 version
        'https://github.com/ljean/coop_cms.git@1139d22bb110052a5ab23ce6e3f830ed835e5a5f#egg=apidev_coop_cms',
        'https://github.com/ljean/coop_html_editor.git@75ea6a776e70cff43758e2d14282196b8defd158#egg=coop_html_editor',

    ],
    long_description=open('README.rst').read(),
    url='https://github.com/ljean/balafon',
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
