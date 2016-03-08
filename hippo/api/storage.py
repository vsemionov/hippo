from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import Storage
from django.utils.encoding import force_unicode

from pymongo import MongoClient
from gridfs import GridFS, NoFile


class GridFSStorage(Storage):
    URL_PREFIX = '/files/'

    DEFAULT_CONFIG = {
        'HOST': 'localhost',
        'PORT': 27017,
        'DB': 'admin',
        'AUTH_DB': 'admin',
        'USER': '',
        'PASS': '',
        'GRIDFS': 'fs',
        'OPTIONS': {
            }
    }

    def __init__(self, host=None, port=None, db=None, auth_db=None, user=None, password=None, collection=None):
        config = self.DEFAULT_CONFIG.copy()
        options = config['OPTIONS'].copy()
        config.update(getattr(settings, 'MONGODB', {}))
        options.update(config['OPTIONS'])
        config['OPTIONS'] = options

        host = host or config['HOST']
        port = port or config['PORT']
        db = db or config['DB']
        auth_db = auth_db or config['AUTH_DB']
        user = user if user is not None else config['USER']
        password = password or config['PASS']
        collection = collection or config['GRIDFS']

        client = MongoClient(host=host, port=port, **options)
        self.db = client[db]
        if user:
            self.db.authenticate(user, password, auth_db)
        self.fs = GridFS(self.db, collection=collection)

    def _open(self, name, mode='rb'):
        return GridFSFile(name, self, mode=mode)

    def _save(self, name, content):
        name = force_unicode(name).replace('\\', '/')
        content.open()
        try:
            kwargs = {'filename': name}
            if hasattr(content.file, 'content_type'):
                kwargs['content_type'] = content.file.content_type
            with self.fs.new_file(**kwargs) as gfile:
                if hasattr(content, 'chunks'):
                    for chunk in content.chunks():
                        gfile.write(chunk)
                else:
                    gfile.write(content)
        finally:
            content.close()
        return name

    def get_valid_name(self, name):
        return force_unicode(name).strip().replace('\\', '/')

    def delete(self, name):
        f = self._open(name, 'r')
        return self.fs.delete(f.file._id)

    def exists(self, name):
        try:
            self.fs.get_last_version(name)
            return True
        except NoFile:
            return False

    def listdir(self, path):
        return ((), self.fs.list())

    def size(self, name):
        try:
            return self.fs.get_last_version(name).length
        except NoFile:
            raise ValueError('File with name "%s" does not exist' % name)

    def url(self, name):
        return '%s%s' % (self.URL_PREFIX, name)


class GridFSFile(File):
    def __init__(self, name, storage, mode):
        self.name = name
        self._storage = storage
        self._mode = mode

        try:
            self.file = storage.fs.get_last_version(name)
        except NoFile:
            raise ValueError("The file doesn't exist.")

    @property
    def closed(self):
        return False

    def open(self, mode=None):
        if mode and mode != self._mode:
            raise ValueError("The file cannot be reopened.")
        self.file.seek(0)

    @property
    def size(self):
        return self.file.length

    def read(self, num_bytes=None):
        return self.file.read(num_bytes)

    def write(self, content):
        raise NotImplementedError()

    def close(self):
        self.file.close()
