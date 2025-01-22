from google.cloud import datastore, storage
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize clients
datastore_client = datastore.Client()
storage_client = storage.Client()

# Default bucket name
DEFAULT_BUCKET_NAME = 'proj1-rn'

def list_db_entries():
    """List entries in the Datastore 'photos' kind."""
    query = datastore_client.query(kind="photos")
    photos = query.fetch()
    for photo in photos:
        logging.info(photo.items())

def add_db_entry(photo_data):
    """Add an entry to the Datastore."""
    entity = datastore.Entity(key=datastore_client.key('photos'))
    entity.update(photo_data)
    datastore_client.put(entity)
    logging.info(f"Added photo with data: {photo_data}")

def fetch_db_entry(filters):
    """Fetch entries from Datastore that match the given filters."""
    query = datastore_client.query(kind='photos')
    for attr, value in filters.items():
        query.add_filter(attr, "=", value)
    results = list(query.fetch())
    logging.info(f"Fetched {len(results)} entries for filters {filters}")
    return results

def get_list_of_files(bucket_name=DEFAULT_BUCKET_NAME):
    """List all files in a specified bucket."""
    blobs = storage_client.list_blobs(bucket_name)
    files = [blob.name for blob in blobs]
    logging.info(f"Files in {bucket_name}: {files}")
    return files

def upload_file(file_name, bucket_name=DEFAULT_BUCKET_NAME):
    """Upload a file to a specified bucket."""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_filename(file_name)
        logging.info(f"Uploaded file {file_name} to bucket {bucket_name}")
    except Exception as e:
        logging.error(f"Failed to upload file: {str(e)}")

def download_file(file_name, bucket_name=DEFAULT_BUCKET_NAME):
    """Download a file from a specified bucket."""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.download_to_filename(file_name)
        logging.info(f"Downloaded {file_name} from {bucket_name}. Info: Size: {blob.size} bytes, Content-type: {blob.content_type}")
    except Exception as e:
        logging.error(f"Failed to download file: {str(e)}")

def delete_file(file_name, bucket_name=DEFAULT_BUCKET_NAME):
    """Delete a file from a specified bucket."""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.delete()
        logging.info(f"Deleted {file_name} from {bucket_name}.")
    except Exception as e:
        logging.error(f"Failed to delete file: {str(e)}")

if __name__ == '__main__':
    # Example Usage
    list_db_entries()
    photo_data = {"name":"fau-rocks.jpeg", "url":"blablabla.com/ricardo.jpeg", "user":"rdeandrade", 'timestamp':int(time.time())}
    add_db_entry(photo_data)
    filters = {'user':'rdeandrade'}
    results = fetch_db_entry(filters)
    logging.info(f"Results: {results}")
