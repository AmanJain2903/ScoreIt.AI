import mongomock
import pytest
from db.bulk_update import addToCollection, deleteFromCollection

pytestmark = pytest.mark.unit

# Sample test data
@pytest.fixture
def mock_collection():
    client = mongomock.MongoClient()
    db = client["test_db"]
    collection = db["test_users"]
    collection.insert_many([
        {"email": "a@example.com", "name": "Alice"},
        {"email": "b@example.com", "name": "Bob"}
    ])
    return collection

def test_add_to_collection(mock_collection):
    fields_to_add = {"dark_mode": False}
    addToCollection(mock_collection, fields_to_add)

    # Assert all docs now contain "dark_mode": False
    all_docs = list(mock_collection.find({}))
    for doc in all_docs:
        assert "dark_mode" in doc
        assert doc["dark_mode"] is False

def test_delete_from_collection(mock_collection):
    # First, add a field
    mock_collection.update_many({}, {"$set": {"dark_mode": False}})
    
    # Now delete it
    fields_to_remove = {"dark_mode": ""}
    deleteFromCollection(mock_collection, fields_to_remove)

    # Assert all docs no longer contain "dark_mode"
    all_docs = list(mock_collection.find({}))
    for doc in all_docs:
        assert "dark_mode" not in doc