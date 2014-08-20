from setuptools import setup, find_packages
import subprocess
from icybackup import __version__

def get_long_desc():
    """Use Pandoc to convert the readme to ReST for the PyPI."""
    try:
        return subprocess.check_output(['pandoc', '-f', 'markdown', '-t', 'rst', 'README.mdown'])
    except:
        print "WARNING: The long readme wasn't converted properly"

setup(
    name='django-icybackup-jl',
    version=__version__,
    description='A Django database/media backup tool with Amazon Glacier and local folder support',
    long_description=get_long_desc(),
    author='Jaroslaw Lachowski',
    author_email='jalachowski@gmail.com',
    url='https://github.com/jlachowski/django-icybackup',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=[
        'setuptools_git>=0.3',
    ],
    install_requires=[
        'boto',
        'python-dateutil',
    ],
)
