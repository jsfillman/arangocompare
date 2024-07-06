import os
from .client import ArangoDBClient
from .comparator import compare_databases

if __name__ == "__main__":
    if os.getenv("ENV") == "production":
        db1_config = {
            "url": os.getenv("ARANGO_URL1", "http://localhost:8529"),
            "username": os.getenv("ARANGO_USERNAME1", "root"),
            "password": os.getenv("ARANGO_PASSWORD1", "password"),
            "db_name": os.getenv("ARANGO_DB_NAME1", "test_db1")
        }

        db2_config = {
            "url": os.getenv("ARANGO_URL2", "http://localhost:8529"),
            "username": os.getenv("ARANGO_USERNAME2", "root"),
            "password": os.getenv("ARANGO_PASSWORD2", "password"),
            "db_name": os.getenv("ARANGO_DB_NAME2", "test_db2")
        }

        log_dir = os.getenv("LOGFILE_OUT", "/logs")

        client1 = ArangoDBClient(**db1_config)
        client2 = ArangoDBClient(**db2_config)

        summary1 = client1.get_summary()
        summary2 = client2.get_summary()

        compare_databases(client1, client2, summary1, summary2, log_dir)
    else:
        print("Development mode: Build successful")
