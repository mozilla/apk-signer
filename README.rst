==========
APK Signer
==========

Mozilla's APK signing library and service

Description
===========

The APK signing service is responsible for signing APK (Android package) files
with developer keys so that the APKs can be integrated securely into the Android
ecosystem.

See also:

* `APK Factory Service <https://github.com/mozilla/apk-factory-service>`_
* `APK Factory Library <https://github.com/mozilla/apk-factory-library>`_

Developer Setup
===============

Set yourself up for local development using Python 2.7 and
a `virtualenv`_ (recommended: `virtualenvwrapper`_) like::

    git clone git@github.com:mozilla/apk-signer.git
    cd apk-signer
    mkvirtualenv apk-signer
    python setup.py develop
    pip install --no-deps -r requirements/dev.txt

Running Tests
=============

::

    nosetests

Working On Docs
===============

::

    make -C docs/ html

.. _virtualenv: http://www.virtualenv.org/en/latest/
.. _virtualenvwrapper: https://pypi.python.org/pypi/virtualenvwrapper
