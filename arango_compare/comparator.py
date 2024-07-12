class Comparator:
    def compare_collections(self, source, target):
        discrepancies = {}
        for name, source_info in source.items():
            if name not in target:
                discrepancies[name] = 'Missing in target'
            else:
                target_info = target[name]
                if source_info != target_info:
                    discrepancies[name] = {
                        'source': source_info,
                        'target': target_info
                    }
        for name in target:
            if name not in source:
                discrepancies[name] = 'Missing in source'
        return discrepancies

    def compare_indexes(self, source_indexes, target_indexes):
        discrepancies = {}
        for id, source_info in source_indexes.items():
            if id not in target_indexes:
                discrepancies[id] = 'Missing in target'
            else:
                target_info = target_indexes[id]
                if source_info != target_info:
                    discrepancies[id] = {
                        'source': source_info,
                        'target': target_info
                    }
        for id in target_indexes:
            if id not in source_indexes:
                discrepancies[id] = 'Missing in source'
        return discrepancies

    def compare_entities(self, source_entities, target_entities):
        discrepancies = {}
        collection_discrepancies = self.compare_collections(source_entities['collections'], target_entities['collections'])
        if collection_discrepancies:
            discrepancies['collections'] = collection_discrepancies

        index_discrepancies = {}
        for coll_name, source_indexes in source_entities['indexes'].items():
            target_indexes = target_entities['indexes'].get(coll_name, {})
            index_discrepancies[coll_name] = self.compare_indexes(source_indexes, target_indexes)
        if any(index_discrepancies.values()):
            discrepancies['indexes'] = index_discrepancies

        return discrepancies
