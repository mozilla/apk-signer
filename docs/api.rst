===
API
===

Here is the web API offered by the APK Signer.
Here are some URLs where you can find a deployed APK Signer:

**production**
    https://apk-signer.mozilla.org

**stage**
    https://apk-signer.allizom.org

Authentication
==============

All incoming and outgoing requests are secured by a `Hawk`_ shared key.
The setting ``HAWK_CREDENTIALS`` is a dictionary of consumers and credentials.
The following credentials are defined for use:

**apk-factory**
    The APK Factory will communicate with the signing service to sign APKs.
    All incoming requests to the signer must be signed with these
    credentials. As per Hawk, the server signs its response using the same
    credentials that the request was signed with.

.. _Hawk: https://github.com/hueniverse/hawk

Endpoints
=========


.. http:post:: /sign

    This endpoint accepts an unsigned APK file and returns a new APK file that
    has been signed with an Android key store.
    This signing process works just like the standard
    `Android signing process`_.
    This API accepts standard ``application/x-www-form-urlencoded`` POST
    parameters.

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

        {
            "signed_apk_s3_url": "https://amazon-s3/path/to/signed/file.apk",
        }

    :status 200: success.
    :status 400: request was invalid.
    :status 401: authentication error.

.. _`Android signing process`: http://developer.android.com/tools/publishing/app-signing.html
