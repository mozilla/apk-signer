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
    pip install --no-deps -r requirements/dev.txt

Make sure you create a local settings file::

    cp apk_signer/settings/local.py-dist apk_signer/settings/local.py

Running Tests
=============

::

    ./manage.py test

This uses `django-nose`_ so you can do all the `nose`_ things you're probably
used to.

Running A development server
============================

::

    ./manage.py runserver

Then open http://127.0.0.1:8000/

Working On Docs
===============

::

    make -C docs/ html

.. _django-nose: https://github.com/django-nose/django-nose
.. _nose: https://nose.readthedocs.org/en/latest/
.. _virtualenv: http://www.virtualenv.org/en/latest/
.. _virtualenvwrapper: https://pypi.python.org/pypi/virtualenvwrapper
