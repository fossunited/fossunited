from setuptools import find_packages, setup

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in fossu_platform/__init__.py
from fossu_platform import __version__ as version

setup(
	name="fossu_platform",
	version=version,
	description="Built on Frappe",
	author="Frappe x FOSSUnited",
	author_email="developers@frappe.io",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
)
