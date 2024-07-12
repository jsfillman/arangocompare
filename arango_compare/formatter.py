class Formatter:
    def format_collections(self, collections):
        formatted = {}
        for collection in collections:
            formatted[collection['name']] = {
                'count': collection['count'],
                'status': collection['status']
            }
        return formatted

    def format_indexes(self, indexes):
        formatted = {}
        for index in indexes:
            formatted[index['id']] = {
                'type': index['type'],
                'fields': index['fields'],
                'unique': index.get('unique', False),
                'sparse': index.get('sparse', False)
            }
        return formatted

    def format_entities(self, entities):
        formatted_entities = {}
        formatted_entities['collections'] = self.format_collections(entities['collections'])
        formatted_entities['indexes'] = {
            coll_name: self.format_indexes(indexes)
            for coll_name, indexes in entities['indexes'].items()
        }
        return formatted_entities
