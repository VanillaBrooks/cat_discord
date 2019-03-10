import subprocess
import sys
from setuptools import setup, find_packages


# this is main directory

with open('requirements.txt', 'r') as f:
	pkg_install = f.read().split()


setup(
	name='cat_discord',
	version='0.0.1',
	packages=[''],
	install_requires=pkg_install,
	include_package_data=True,
	zip_safe=False,
)

