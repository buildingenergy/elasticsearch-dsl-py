from datetime import datetime

from elasticsearch_dsl import DocType, Field

user_field = Field('object')
user_field.property('name', 'string', fields={'raw': Field('string', index='not_analyzed')})

class Repository(DocType):
    owner = user_field
    created_at = Field('date')
    description = Field('string', analyzer='snowball')
    tags = Field('string', index='not_analyzed')

    class Meta:
        index = 'git'
        doc_type = 'repos'

def test_get(data_client):
    elasticsearch_repo = Repository.get('elasticsearch-dsl-py')

    assert isinstance(elasticsearch_repo, Repository)
    assert elasticsearch_repo.owner.name == 'elasticsearch'

def test_save_updates_existing_doc(data_client):
    elasticsearch_repo = Repository.get('elasticsearch-dsl-py')

    elasticsearch_repo.created_at = datetime(2014, 1, 1)
    assert not elasticsearch_repo.save()

    new_repo = data_client.get(index='git', doc_type='repos', id='elasticsearch-dsl-py')
    assert '2014-01-01T00:00:00' == new_repo['_source']['created_at']

def test_can_save_to_different_index(client):
    test_repo = Repository(description='testing', id=42)
    assert test_repo.save(index='test-document')

    assert {
        'found': True,
        '_index': 'test-document',
        '_type': 'repos',
        '_id': '42',
        '_version': 1,
        '_source': {'description': 'testing'},
    } == client.get(index='test-document', doc_type='repos', id=42)


def test_search(data_client):
    assert Repository.search().count() == 1

def test_search_returns_proper_doc_classes(data_client):
    result = Repository.search().execute()

    elasticsearch_repo = result.hits[0]

    assert isinstance(elasticsearch_repo, Repository)
    assert elasticsearch_repo.owner.name == 'elasticsearch'