import unittest
from alsdkdefs.persistent_storage import PersistentStorage
from alsdkdefs import SpecCache
from alsdkdefs import ServiceDefinition


class MyTestCase(unittest.TestCase):
    def test_ps(self):
        stor = PersistentStorage('test_persistent_storage')
        stor.clear()
        assert stor.get('a_key') is None
        assert stor.get('a_key', 123) == 123
        stor.set('a_key', 'stored')
        assert stor.get('a_key') == 'stored'
        stor.set('a_key', 'stored2')
        assert stor.get('a_key') == 'stored2'
        assert isinstance(stor.created_at('a_key'), int)
        stor.set('tuple', (1, 2, 3))
        assert stor.get('tuple') == (1, 2, 3)
        dictionary = {'a': 'b', 'b': 1, 'c': (1, 2, 3)}
        stor.set('dict', dictionary)
        assert stor.get('dict') == dictionary
        assert sorted(stor.list()) == sorted(['a_key', 'dict', 'tuple'])
        stor.delete('tuple')
        assert sorted(stor.list()) == sorted(['a_key', 'dict'])
        stor.clear()
        assert stor.list() == []

    def test_spec_stor(self):
        sample_spec = {'key': 'value', 'key2': 'val2'}
        service_def = ServiceDefinition('test_service', '/tmp/fake', 'public')
        cache = SpecCache(service_def, 'v0.0.1', lambda x: {'key': 'value', 'key2': x}, ['val2'])
        assert cache.get_spec() == sample_spec
        assert cache.list() == ['test_service_public_v0.0.1']
        assert cache.get('test_service_public_v0.0.1') == sample_spec
        del cache
        new_spec = {'key1': 'value', 'key3': 'val2'}
        cache = SpecCache(service_def, 'v0.0.1', lambda x: {'key1': 'value', 'key3': x}, ['val2'])
        assert cache.get_spec() == sample_spec
        del cache
        cache = SpecCache(service_def, 'v0.0.2', lambda x: {'key1': 'value', 'key3': x}, ['val2'])
        assert cache.get_spec() == new_spec
        assert cache.list() == ['test_service_public_v0.0.2']

if __name__ == '__main__':
    unittest.main()
