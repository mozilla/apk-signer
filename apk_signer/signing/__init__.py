"""
Handles all the finicky aspects of APK signing

"""
import hashlib
import os
import os.path
import subprocess
import tempfile

from django.conf import settings

from apk_signer import storage


class SigningError(Exception):
    # FIXME Add stderr for failed subprocess calls
    """Encapsulates all signing errors"""


def keyhash(webapp_manifest_url):
    return hashlib.sha1(webapp_manifest_url).hexdigest()


def generate(webapp_manifest_url):
    """
    Generates a new key using Java's command line utility keytool

    The resulting command line:

    keytool -genkey
            -keystore <hash of webapp manifest URL provided>.p12
            -storepass mozilla
            -alias 0
            -validity <10 years>
            -keyalg RSA
            -keysize 2048
            -storetype pkcs12
            -dname "CN=Generated key for <webapp_manifest_url>, OU=Mozilla APK Factory, O=Mozilla Marketplace, L=Mountain View, ST=California, C=US"
    """

    # Generate the dname from the template
    # FIXME This should really come from Django settings, probably
    dname = ["CN=Generated key for {url}".format(url=webapp_manifest_url),
             "OU=Mozilla APK Factory",
             "O=Mozilla Marketplace",
             "L=Mountain View",
             "ST=California",
             "C=US"]
    keystore = os.path.join(getattr(settings, 'APK_SIGNER_KEYS_TEMP_DIR',
                                    tempfile.gettempdir()),
                            keyhash(webapp_manifest_url))
    args = [os.path.join(getattr(settings, 'APK_SIGN_JAVA_CLI_PATH', ''),
                         "keytool"),
            '-genkey',
            '-keystore', keystore,
            '-storepass', getattr(settings, 'APK_SIGNER_STORE_PASSWD',
                                  'mozilla'),
            '-alias', '0',
            '-validity', str(int(getattr(settings, 'APK_SIGNER_VALIDITY_PERIOD',
                                         365 * 10))),
            '-keyalg', getattr(settings, 'APK_SIGNER_APP_KEY_ALGO', 'RSA'),
            '-keysize', str(int(getattr(settings, 'APK_SIGNER_APP_KEY_LENGTH',
                                        2048))),
            '-storetype', 'pkcs12',
            '-dname', ', '.join(dname)]

    # Capture stdout and stderr for logging because Java or keytool seems to be
    # inconsistent about which it writes error messages to.
    stderr, stdout = tempfile.TemporaryFile(), tempfile.TemporaryFile()
    rc = subprocess.call(args, stderr=stderr, stdout=stdout)
    if rc != 0:
        stdout.seek(0)
        stderr.seek(0)
        raise SigningError("Failed to generate key: {url}\nSTDOUT: {stdout}\n"
                           "STDERR: {stderr}\n"
                           .format(url=webapp_manifest_url,
                                   stderr=stderr.read(),
                                   stdout=stdout.read()))
    stderr.close()
    stdout.close()

    # We should really verify that the certificate in the keystore has the
    # dname that we expect but there's no quick way to do that with the Java
    # command line tools.  It should be easily possible with M2Crypto but I'm
    # not certain that we want to install that.

    # Store key in S3
    fp = open(keystore, 'rb')
    try:
        storage.put_app_key(fp, keyhash(webapp_manifest_url))
    except storage.AppKeyAlreadyExists, e:
        raise SigningError("Collision when generating key for {url}: {exc}"
                           .format(url=webapp_manifest_url, exc=e))

    return fp


def lookup(webapp_manifest_url):
    """
    Looks in S3 for an existing key for the manifest URL.  If not found,
    generates a new one, stores in S3, and then attempts fetches from S3.
    """
    try:
        return storage.get_app_key(webapp_manifest_url)
    except storage.NoSuchKey:
        generate(webapp_manifest_url)
        return storage.get_app_key(webapp_manifest_url)


def sign(webapp_manifest_url, apk_fp):
    """
    Signs the JAR file provided by apk_fp.name via the jarsigner CLI
    """
    key_fp = lookup(webapp_manifest_url)

    args = [os.path.join(getattr(settings, 'APK_SIGNER_JAVA_CLI_PATH', ''),
                         "jarsigner"),
            '-sigalg', getattr(settings, 'APK_SIGNER_SIGN_SIG_ALGO',
                               'SHA1withRSA'),
            '-digestalg', getattr(settings, 'APK_SIGNER_SIGN_DIGEST_ALGO',
                                  'SHA1'),
            '-storetype', 'pkcs12',
            '-storepass', getattr(settings, 'APK_SIGNER_STORE_PASSWD',
                                  'mozilla'),
            '-keystore', key_fp.name,
            apk_fp.name, '0']

    # Capture stdout and stderr for logging because Java or keytool seems to be
    # inconsistent about which it writes error messages to.
    stderr, stdout = tempfile.TemporaryFile(), tempfile.TemporaryFile()
    rc = subprocess.call(args, stderr=stderr, stdout=stdout)
    if rc != 0:
        stdout.seek(0)
        stderr.seek(0)
        raise SigningError("Failed to sign APK: {url}\nSTDOUT: {stdout}\n"
                           "STDERR: {stderr}\n"
                           .format(url=webapp_manifest_url,
                                   stderr=stderr.read(),
                                   stdout=stdout.read()))
    stderr.close()
    stdout.close()

    # If key_fp isn't a temporary file, make sure we unlink it
    if type(key_fp) == file:
        os.unlink(key_fp.name)
    # Might be necessary to properly upload for storage.put_signed_apk to
    # function precitably
    apk_fp.seek(0)
    return True
