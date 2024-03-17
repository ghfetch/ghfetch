#!/usr/bin/env python

from setuptools import setup

setup(name='ghfetch-pip',
      version='1.5.3',
      description='CLI tool to fetch GitHub information',
      author='Nullgaro, Icutum',
      author_email='ghfetch.contact@gmail.com',
      url='https://github.com/ghfetch/ghfetch',
      packages=['ghfetch', 'ghfetch.data'],
      install_requires=['pillow', 'aiohttp', 'rich'],
      package_data={'': ['./data/language-colors.json', './LICENSE', './README.md']},
      include_package_data=True,
      entry_points={
        'console_scripts': [
            'ghfetch=ghfetch.main:main'
        ]
    },
    )