from setuptools import setup, find_packages
import os

setup(
        packages = ['convert'],
        entry_points = {
            'console_scripts': ['megadltconvert=convert.dltconvert:main']
            }
        )
