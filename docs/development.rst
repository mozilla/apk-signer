===============
Development
===============

Here's a guide for how to hack on the APK Signer project.

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
