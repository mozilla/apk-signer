"""
Handles all the finicky aspects of APK signing

"""
import os
import os.path
import subprocess
import tempfile
import uuid

from django.conf import settings

from apk_signer import storage
from apk_signer.storage import AppKeyAlreadyExists, NoSuchKey


class SigningError(Exception):
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

    # TODO: delete keystores after use!
    keystore = os.path.join(settings.APK_SIGNER_KEYS_TEMP_DIR,
                            'gen_keystore_{u}'.format(u=uuid.uuid4()))
    args = [
        '-genkey',
        '-keystore', keystore,
        '-storepass', settings.APK_SIGNER_STORE_PASSWD,
        '-alias', '0',
        '-validity', str(int(getattr(settings, 'APK_SIGNER_VALIDITY_PERIOD',
                                     365 * 10))),
        '-keyalg', getattr(settings, 'APK_SIGNER_APP_KEY_ALGO', 'RSA'),
        '-keysize', str(int(getattr(settings, 'APK_SIGNER_APP_KEY_LENGTH',
                                    2048))),
        '-storetype', 'pkcs12',
        '-dname', ', '.join(dname)]

    try:
        keytool(args)
    except KeytoolError, exc:
        raise SigningError("Failed to generate key: ID {id}: {exc}"
                           .format(id=apk_id, exc=exc))

    # TODO: verify cert.
    # We should really verify that the certificate in the keystore has the
    # dname that we expect but there's no quick way to do that with the Java
    # command line tools.  It should be easily possible with M2Crypto but I'm
    # not certain that we want to install that.
    return keystore


def make_keystore(apk_id):
    fp = open(gen_keystore(apk_id), 'rb')
    try:
        storage.put_app_key(fp, apk_id)
    except AppKeyAlreadyExists, e:
        raise SigningError("Collision when generating key for ID {id}: "
                           "{exc}".format(id=apk_id, exc=e))
    fp.seek(0)
    return fp


def get_keystore(apk_id):
    """
    Returns an open file object for a key store.
    A keystore will be generated and saved to S3 if it doesn't exist.
    """
    try:
        return storage.get_app_key(apk_id)
    except NoSuchKey:
        return make_keystore(apk_id)


def sign(apk_id, apk_fp):
    """
    Signs the JAR file provided by apk_fp.name via the jarsigner CLI
    """
    key_fp = get_keystore(apk_id)
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


def find_executable(name):
    path = os.path.join(settings.APK_SIGNER_JAVA_CLI_PATH, name)
    if os.path.exists(path):
        return path
    for p in os.environ['PATH'].split(':'):
        # Don't actually build a new path, just check to make sure we got it.
        if os.path.exists(os.path.join(p, name)):
            return name
    raise EnvironmentError(
        'Cannot find executable "{name}" on $PATH or in '
        'settings.APK_SIGNER_JAVA_CLI_PATH'.format(name=name))


def keytool(args):
    args.insert(0, find_executable('keytool'))
    sp, output = cmd(args)
    if sp.returncode != 0:
        raise KeytoolError('{prog} failed: {out}\n'
                           .format(prog=args[0], out=output))
    return output


def jarsigner(args):
    args.insert(0, find_executable('jarsigner'))
    sp, output = cmd(args)
    if sp.returncode != 0:
        raise JarSignerError('{prog} failed: {out}\n'
                             .format(prog=args[0], out=output))
    return output


def cmd(args):
    sp = subprocess.Popen(args, stderr=subprocess.STDOUT,
                          stdout=subprocess.PIPE)
    output, _ = sp.communicate()
    return sp, output


class JarSignerError(Exception):
    pass


class KeytoolError(Exception):
    pass
