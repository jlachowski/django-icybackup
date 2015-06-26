# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from icybackup import __version__


dependencies = ['boto', 'python-dateutil', 'future'],


setup(
    name='django-icybackup-jl',
    version=__version__,
    description='A Django database/media backup tool with Amazon Glacier and local folder support',
    long_description='A Django database/media backup tool with Amazon Glacier and local folder support',
    author='Jaroslaw Lachowski',
    author_email='jalachowski@gmail.com',
    url='https://github.com/jlachowski/django-icybackup',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['setuptools_git>=0.3', 'future'],
    install_requires=dependencies,
)
