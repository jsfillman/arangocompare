import requests

class ArangoDBClient:
    def __init__(self, base_url, db_name):
        self.base_url = base_url
        self.db_name = db_name

    def get_all_entities(self):
        # Fetch collections
        url_collections = f"{self.base_url}/_db/{self.db_name}/_api/collection"
        response_collections = requests.get(url_collections)
        response_collections.raise_for_status()
        collections = response_collections.json()['result']

        entities = {'collections': collections, 'indexes': {}}

        # Fetch indexes for each collection
        for collection in collections:
            collection_name = collection['name']
            url_indexes = f"{self.base_url}/_db/{self.db_name}/_api/index?collection={collection_name}"
            response_indexes = requests.get(url_indexes)
            response_indexes.raise_for_status()
            indexes = response_indexes.json()['indexes']
            entities['indexes'][collection_name] = indexes

        return entities

    def get_summary(self):
        # If get_summary is needed, implement it here
        pass
