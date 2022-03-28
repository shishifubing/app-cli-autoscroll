#!/usr/bin env python3
# https://setuptools.pypa.io/en/latest/userguide/quickstart.html

from pathlib import Path
from setuptools import setup, find_packages

# The directory containing this file
HERE = Path(__file__).parent

# The text of the README file
README = (HERE / 'README.md').read_text()

# This call to setup() does all the work
setup(
    name='autoscroll',
    version='1.0.0',
    description='Enables universal autoscroll',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/kongrentian/autoscroll',
    author='kongrentian',
    author_email='causelesscause@gmail.com',
    license='GNU General Public License v3.0',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent'],
    packages=find_packages(where='.'),
    include_package_data=True,
    install_requires=['pynput'],
    extras_require={'icon': ['pyside6']},
    entry_points={'console_scripts': ['autoscroll = autoscroll.main:start']},
    python_requires='>=3.6')
