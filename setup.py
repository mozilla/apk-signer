import os

from setuptools import setup, find_packages


setup(name='apk_signer',
      version='0.0.1',
      description="Mozilla's APK signing library and service",
      long_description='',
      author='Kumar McMillan, Ryan Tilder, and contributors',
      author_email='',
      license='MPL 2.0 (Mozilla Public License)',
      url='https://github.com/mozilla/apk-signer',
      include_package_data=True,
      classifiers=[],
      packages=find_packages(exclude=['tests']),
      # NOTE: you must use pip to install all dependencies.
      install_requires=[])
