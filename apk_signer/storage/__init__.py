import tempfile

from django.conf import settings

from boto.s3.connection import S3Connection


def connect(**kw):
    # TODO: pool connections?
    return S3Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY,
                        **kw)


def bucket(name, conn=None):
    if not conn:
        conn = connect()
    return conn.get_bucket(name)


def get_apk(key_path, conn=None):
    """
    Gets an unsigned APK file.
    """
    if not conn:
        conn = connect()

    return get(conn, settings.S3_APK_BUCKET, key_path, suffix='.apk',
               prefix='tmp_unsigned_')


def get(conn, bkt_name, key_path, suffix='', prefix='', dir=None):
    """
    Save an S3 file to a named temporary file and return an open file handle.

    The temporary file will be deleted when the file is closed.
    """
    bkt = bucket(bkt_name, conn=conn)
    key = bkt.get_key(key_path)
    if not key:
        # TODO: maybe add a retry loop here if we hit this error a lot.
        raise NoSuchKey('Key {path} does not exist in {bkt}'
                        .format(path=key_path, bkt=bkt))
    fp = tempfile.NamedTemporaryFile(suffix=suffix, prefix=prefix, dir=dir)
    key.get_contents_to_file(fp)

    fp.flush()
    fp.seek(0)
    return fp


def put_signed_apk(fp, key_path, conn=None):
    """
    Puts a signed APK file.
    """
    if not conn:
        conn = connect()

    bkt = bucket(settings.S3_APK_BUCKET, conn=conn)
    key = bkt.new_key(key_path)
    key.set_contents_from_file(fp)
    # We'll use S3 publicly as a CDN to stream APKs to clients.
    key.set_acl('public-read')


def get_app_key(key_path, conn=None):
    """
    Gets the keystore for an app.
    """
    if not conn:
        conn = connect()
    return get(conn, settings.S3_KEY_BUCKET, key_path, conn=conn,
               suffix='.p12', dir=settings.APK_SIGNER_KEYS_TEMP_DIR)


def put_app_key(fp, key_path, conn=None):
    """
    Puts the keystore for an app.
    """
    if not conn:
        conn = connect()

    bkt = bucket(settings.S3_KEY_BUCKET, conn=conn)
    if bkt.get_key(key_path) is not None:
        raise AppKeyAlreadyExists('App signing key {path} already exists in '
                                  '{bkt}'.format(path=key_path, bkt=bkt))
    key = bkt.new_key(key_path)
    key.set_contents_from_file(fp)
    key.set_acl('private')


class NoSuchKey(Exception):
    """The S3 key path does not exist"""


class AppKeyAlreadyExists(Exception):
    """An S3 entry already exists for that app key path"""
