from setuptools import find_packages, setup

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in fossunited/__init__.py
from fossunited import __version__ as version

setup(
	name="fossunited",
	version=version,
	description="Built on Frappe",
	author="Frappe x FOSSUnited",
	author_email="developers@frappe.io",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
)
