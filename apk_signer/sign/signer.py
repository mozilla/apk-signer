"""
Handles all the finicky aspects of APK signing

"""
import os
import os.path
import subprocess
import tempfile
import uuid

from django.conf import settings

from commonware.log import getLogger

from apk_signer import storage
from apk_signer.base import get_user_mode
from apk_signer.storage import AppKeyAlreadyExists, NoSuchKey

log = getLogger(__name__)


class SigningError(Exception):
    """Encapsulates all signing errors"""


def gen_keystore(apk_id):
    """
    Generates a new key store using Java's keytool command.
    """

    mode = get_user_mode()
    log.info('generating key store for app ID {id} in '
             '{mode} mode'.format(mode=mode, id=apk_id))

    # -dname = distinguished name
    # CN = common name
    # OU = organizational unit
    dname = ["CN={mode}: Marketplace app ID {id}".format(id=apk_id,
                                                         mode=mode),
             "OU={mode}: Mozilla APK Signer".format(mode=mode),
             "O=Firefox Marketplace",
             "L=Mountain View",
             "ST=California",
             "C=US"]

    # TODO: delete keystores after use! bug 976295
    keystore = os.path.join(settings.APK_SIGNER_KEYS_TEMP_DIR,
                            'gen_keystore_{u}'.format(u=uuid.uuid4()))

    if mode == 'REVIEWER':
        validity = settings.APK_REVIEWER_VALIDITY_PERIOD
    else:
        validity = settings.APK_END_USER_VALIDITY_PERIOD

    args = [
        '-genkey',
        '-keystore', keystore,
        '-storepass', settings.APK_SIGNER_STORE_PASSWD,
        # We currently aren't using aliases. This flag is intended for having
        # multiple key pairs in the same keystore.
        '-alias', '0',
        '-validity', str(validity),
        '-keyalg', settings.APK_SIGNER_APP_KEY_ALGO,
        '-keysize', str(settings.APK_SIGNER_APP_KEY_LENGTH),
        '-storetype', 'pkcs12',
        '-dname', ', '.join(dname)]

    try:
        keytool(args)
    except KeytoolError, exc:
        raise SigningError("Failed to generate key: ID {id}: {exc}"
                           .format(id=apk_id, exc=exc))

    return keystore


def make_keystore(apk_id, store=True):
    fp = open(gen_keystore(apk_id), 'rb')
    if not store:
        # Not saving the key so return it as is.
        return fp

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

    An end-user keystore will be generated and saved to S3 if it doesn't
    exist. Reviewer keystores are always generated.
    """
    if get_user_mode() == 'REVIEWER':
        log.info('reviewer mode: generating a new keystore')
        # Always generate new key stores for reviewers.
        # Thus, we don't need to store them.
        return make_keystore(apk_id, store=False)
    else:
        log.info('end-user mode: fetching/generating/storing keystore')
        try:
            # TODO: maybe check for expired key stores. In other words,
            # this code will break in 10 years :)
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
    finally:
        key_fp.close()
        # Remove the temporary key store we downloaded from S3 so
        # it's not sitting around on the server.
        os.unlink(key_fp.name)

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
