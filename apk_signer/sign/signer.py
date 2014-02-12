"""
Handles all the finicky aspects of APK signing

"""
import os
import os.path
import subprocess
import tempfile

from django.conf import settings

from apk_signer import storage


class SigningError(Exception):
    # FIXME Add stderr for failed subprocess calls
    """Encapsulates all signing errors"""


def gen_keystore(apk_id):
    """
    Generates a new key using Java's command line utility keytool

    The resulting command line:

    keytool -genkey
            -keystore <apk_id>.p12
            -storepass mozilla
            -alias 0
            -validity <10 years>
            -keyalg RSA
            -keysize 2048
            -storetype pkcs12
            -dname "CN=Generated key for <apk_id>, OU=Mozilla APK Factory, O=Mozilla Marketplace, L=Mountain View, ST=California, C=US"
    """

    # Generate the dname from the template
    # FIXME This should really come from Django settings, probably
    dname = ["CN=Generated key for ID {id}".format(id=apk_id),
             "OU=Mozilla APK Factory",
             "O=Mozilla Marketplace",
             "L=Mountain View",
             "ST=California",
             "C=US"]
    # TODO: make keystore a named tempfile.
    keystore = os.path.join(settings.APK_SIGNER_KEYS_TEMP_DIR, apk_id)
    args = [os.path.join(settings.APK_SIGNER_JAVA_CLI_PATH, "keytool"),
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
    # TODO: switch to using subprocess pipes.
    stderr, stdout = tempfile.TemporaryFile(), tempfile.TemporaryFile()
    rc = subprocess.call(args, stderr=stderr, stdout=stdout)
    if rc != 0:
        stdout.seek(0)
        stderr.seek(0)
        raise SigningError("Failed to generate key: ID: {id}\n"
                           "STDOUT: {stdout}\n"
                           "STDERR: {stderr}\n"
                           .format(id=apk_id,
                                   stderr=stderr.read(),
                                   stdout=stdout.read()))
    stderr.close()
    stdout.close()

    # We should really verify that the certificate in the keystore has the
    # dname that we expect but there's no quick way to do that with the Java
    # command line tools.  It should be easily possible with M2Crypto but I'm
    # not certain that we want to install that.
    return keystore


def make_keystore(apk_id):
    keystore = gen_keystore(apk_id)

    # Store key in S3
    # TODO: yield file so that file handle gets closed.
    fp = open(keystore, 'rb')
    try:
        storage.put_app_key(fp, apk_id)
    except storage.AppKeyAlreadyExists, e:
        raise SigningError("Collision when generating key for ID {id}: {exc}"
                           .format(id=apk_id, exc=e))

    return fp


def lookup(apk_id):
    """
    Looks in S3 for an existing key for the manifest URL.  If not found,
    generates a new one, stores in S3, and then attempts fetches from S3.
    """
    try:
        return storage.get_app_key(apk_id)
    except storage.NoSuchKey:
        make_keystore(apk_id)
        return lookup(apk_id)


def sign(apk_id, apk_fp):
    """
    Signs the JAR file provided by apk_fp.name via the jarsigner CLI
    """
    key_fp = lookup(apk_id)
    signed_fp = tempfile.NamedTemporaryFile(prefix='signed_', suffix='.apk')
    args = ['-sigalg', settings.APK_SIGNER_SIGN_SIG_ALGO,
            '-digestalg', settings.APK_SIGNER_SIGN_DIGEST_ALGO,
            '-storetype', 'pkcs12',
            '-storepass', settings.APK_SIGNER_STORE_PASSWD,
            '-keystore', 'file:{name}'.format(name=key_fp.name),
            '-signedjar', signed_fp.name,
            '-verbose',
            apk_fp.name, '0']
    try:
        jarsigner(args)
    except JarSignerError, exc:
        raise SigningError("Failed to sign APK: ID {id}: {exc}"
                           .format(id=apk_id, exc=exc))

    signed_fp.seek(0)
    return signed_fp


def jarsigner(args):
    args.insert(0, os.path.join(settings.APK_SIGNER_JAVA_CLI_PATH,
                                'jarsigner'))
    sp = subprocess.Popen(args, stderr=subprocess.STDOUT,
                          stdout=subprocess.PIPE)
    output, _ = sp.communicate()
    if sp.returncode != 0:
        raise JarSignerError('{prog} failed: {out}\n'
                             .format(prog=args[0], out=output))
    return output


class JarSignerError(Exception):
    pass
