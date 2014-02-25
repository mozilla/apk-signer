==========
Deployment
==========

Before configuring the app for deployment, read through
:ref:`development`; some concepts may apply.

See ``apk_signer/settings/sites/*`` for site-specific settings files.

The signer can run in two user modes (in Django settings)::

    APK_USER_MODE = 'END_USER'
    APK_USER_MODE = 'REVIEWER'

*REVIEWER mode*
    The signer instance is intended for app reveiwers.
    In this mode APKs are self-signed with a short lived key store.
    Key stores are never re-used.

*END_USER mode*
    The signer instance is intended for end-users on Firefox for Android.
    In this mode APKs are self-signed with a long-lived key store
    that is associated with the app's manifest URL. When an app is
    updated, the same key store is used to sign new APK versions.
