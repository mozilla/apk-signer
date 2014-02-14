===
API
===

Here is the web API offered by the APK Signer.
Here are some URLs where you can find a deployed APK Signer:

**production**
    TBD

**stage**
    https://apk-signer.stage.mozaws.net/


All APIs accept standard ``application/x-www-form-urlencoded`` POST parameters.

Authorization
=============

All incoming and outgoing requests are secured by a `Hawk`_ shared key.
The setting ``HAWK_CREDENTIALS`` is a dictionary of consumers and credentials.
The following credentials are defined for use:

**apk-factory**
    The APK Factory will communicate with the signing service to sign APKs.
    All incoming requests to the signer must be signed with these
    credentials. As per Hawk, the server signs its response using the same
    credentials that the request was signed with.

All Hawk requests must sign their request payload (request body plus request
content-type). If both of these are blank, such as in a GET request,
you must sign them as empty strings.

Authorized API requests will respond with a Hawk header that signs the response,
including payload. For the best security, make sure your client is
authorizing incoming Hawk responses.

Signer
======

.. http:post:: /sign

    This endpoint accepts an unsigned APK file and returns a new APK file that
    has been signed with an Android key store.
    This signing process works just like the standard
    `Android signing process`_.

    **Request**

    :param apk_id:
        A unique identifier for this APK such as one derived from a webapp
        manifest URL. This value will be used as an Amazon S3 storage key.

    :param unsigned_apk_s3_path:
        An Amazon S3 path (in a shared bucket) to the unsigned
        APK file that should be fetched and signed.
        Example: ``/path/to/unsigned/file.apk``.

    :param unsigned_apk_s3_hash:
        A SHA256 content hash (in hex) that can be used to verify the
        contents of the APK file after fetching it from Amazon S3.

    :param signed_apk_s3_path:
        An Amazon S3 path (in a shared bucket) that the final, signed APK file
        should be written to.
        Example: ``/path/to/signed/file.apk``.

    **Response**

    :param signed_apk_s3_url:
        A publicly accessible Amazon S3 URL to the signed APK file.

    Example:

    .. code-block:: json

        {"signed_apk_s3_url": "https://s3.amazonaws.com/bucket/key/to/signed.apk"}

    :status 200: success.
    :status 400: request was invalid.
    :status 403: authentication error.

.. _`Android signing process`: http://developer.android.com/tools/publishing/app-signing.html

System
======

There are some system APIs you can use to monitor the health of the APK Signer
system.


.. http:get:: /system/auth

    This endpoint lets you test your `Hawk`_ client to see that you are making
    authorized GET requests correctly.

.. http:post:: /system/auth

    You can also POST to the same endpoint to test an authorized Hawk request.

    **Response**

    Example response to GET:

    .. code-block:: json

        {"message": "GET authentication successful"}

    Example response to POST:

    .. code-block:: json

        {"message": "POST authentication successful"}

    :status 200: success.
    :status 403: authentication error.


.. http:get:: /system/cef

    A request to this endpoint will log an internal CEF
    (Common Event Format) message.
    This will let you test that the system is hooked up for CEF logging.

    **Response**

    Example:

    .. code-block:: json

        {"message": "CEF messages sent"}

    :status 200: success.


.. http:get:: /system/log

    A request to this endpoint will send a test message to the
    internal logging system.
    This will let you test that the system is hooked up for logging.

    **Response**

    Example:

    .. code-block:: json

        {'message': 'messages logged on server'}

    :status 200: success.


.. http:get:: /system/stats

    A request to this endpoint will increment a `statsd`_ key for testing
    purposes.

    **Response**

    Example:

    .. code-block:: json

        {"message": "apk_signer.system_check incremented"}

    :status 200: success.


.. http:get:: /system/tools

    This endpoint reports whether or not the required command line tools are
    available.

    **Response**

    Example of 200 response:

    .. code-block:: json

        {"detail": {"success": true, "keytool": "ok", "jarsigner": "ok"}}

    Example of 409 response:

    .. code-block:: json

        {"detail": {"success": false, "keytool": "MISSING", "jarsigner": "ok"}}

    :status 200: success.
    :status 409: conflict.


.. http:post:: /system/trace

    A request to this endpoint will trigger an exception to test that
    exceptions are handled correctly.

    **Response**

    N/A

    :status 500: internal error.

.. _`Hawk`: https://github.com/hueniverse/hawk
.. _`statsd`: https://github.com/etsy/statsd/
