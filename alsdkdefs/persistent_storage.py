import pickle
from pathlib import Path
import os
from datetime import datetime
import shutil

DEFAULT_PATH = os.path.join(Path.home(), ".alertlogic", "cache")


class PersistentStorage:
    def __init__(self, namespace, storage_class_id='key_object_file_storage', **kwargs):
        storage_class_selector = {'key_object_file_storage': KeyObjectFileStorage}
        storage_class = storage_class_selector[storage_class_id]
        self.storage = storage_class(namespace, **kwargs)

    def set(self, key, value):
        now = PersistentStorage.__now()
        record = PersistentStorage.__storage_record(key, value, now)
        return self.storage.set(key, record)

    def get(self, key, default=None):
        record = self.storage.get(key)
        if record:
            return PersistentStorage.__get_record_value(record)
        else:
            return default

    def created_at(self, key):
        record = self.storage.get(key)
        if record:
            return PersistentStorage.__get_record_created_at(record)

    def clear(self):
        return self.storage.clear()

    def delete(self, key):
        return self.storage.delete(key)

    def list(self):
        return self.storage.list()

    @staticmethod
    def __storage_record(key, value, created_at):
        return {'key': key, 'value': value, 'created_at': created_at}

    @staticmethod
    def __get_record_value(record):
        return record.get('value')

    @staticmethod
    def __get_record_created_at(record):
        return record.get('created_at')

    @staticmethod
    def __now():
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        return int(timestamp)


class KeyObjectStorage:
    def __init__(self, namespace, **kwargs):
        self.namespace = namespace

    def set(self, key, value):
        pass

    def get(self, key, default=None):
        pass

    def delete(self, key):
        pass

    def list(self):
        pass


class KeyObjectFileStorage(KeyObjectStorage):
    def __init__(self, namespace, **kwargs):
        super().__init__(namespace, **kwargs)
        storage_path = kwargs.get('storage_path', DEFAULT_PATH)
        self.file_storage_path = os.path.join(storage_path, namespace)
        self.__init()

    def __init(self):
        if not os.path.isdir(self.file_storage_path):
            os.makedirs(self.file_storage_path)

    def set(self, key, value):
        with open(self.__key_file(key), 'wb') as f:
            pickle.dump(value, f)

    def get(self, key, default=None):
        try:
            with open(self.__key_file(key), 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return default

    def delete(self, key):
        os.remove(self.__key_file(key))

    def clear(self):
        shutil.rmtree(self.file_storage_path)
        self.__init()

    def list(self):
        return os.listdir(self.file_storage_path)

    def __key_file(self, key):
        return os.path.join(self.file_storage_path, key)
