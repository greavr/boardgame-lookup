from datetime import datetime
import json
import os
import firebase_admin
from firebase_admin import firestore, credentials
from google.cloud import storage
import functions_framework

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    # Validate File uploaded
    try:
        if request.files['file']:
            file_obj = request.files['file']
            file_name = str(file_obj.filename).lower()
            file_content_type = file_obj.content_type
        else:
            print("Missing file object")
            return request.args
    except Exception as ex:
        print(ex)
        return "Missing file for upload"

    if request_json and "game_id" in request_json:
        game_id = request_json["game_id"]
    elif request_args and "game_id" in request_args:
        game_id = request_args["game_id"]
    else:
        print("Missing parameter 'game_id'")
        return "Missing file_name"
    
    if request_json and "doc_type" in request_json:
        doc_type = request_json["doc_type"]
    elif request_args and "game_id" in request_args:
        doc_type = request_args["doc_type"]
    else:
        print("Missing parameter 'doc_type'")
        return "Missing doc_type"
    
    # Validate file type:
    # Validate the file content type
    ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv', 'text/txt'])
    if file_content_type not in ALLOWED_FILE_TYPES:
        print(f'Invalid file type: {file_content_type}')
        return "Unsupported filetype"


    # Upload file to GCS
    try:
        # Check for GCS Bucket ENV variable if missing rage quit
        if os.environ['GCS_BUCKET']:
            bucket_name = os.environ['GCS_BUCKET']
        else:
            print("No GCS_BUCKET Environment variable set")
            return "No GCS_BUCKET Environment variable set"
        
            # Create a storage client
        client = storage.Client()

        # Create a bucket
        bucket = client.bucket(bucket_name)

        # Set metadata
        options = {}
        options['content_type'] = "application/octet-stream"
        path = game_id + '/' + file_name
        print(f"Uploading file: {file_name} to the path: {path}")

        # Upload the file to the bucket
        blob = bucket.blob(path)
        blob.upload_from_string(file_obj.read(), content_type=file_obj.content_type)
        public_url = blob.public_url
        # Grab the public URL
        print(f"Upload Complete: {public_url}")
    except Exception as ex:
        print(ex)
        return (f"Unable to upload to GCS: {ex}")

    # Save record to Firestore
    ## Gather Default Creds
    try:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        now = datetime.now()
        # Add New 
        db.collection("documents").add({"gameid": game_id, "Created": now, "PublicURL" : public_url, "GCSPath" : path, "FileType" : doc_type})
        print("Saved to firestore")
    except Exception as ex:
        print(ex)
        return (f"Unable to Save to Firestore: {ex}")
    
    return json.dumps({"file" : file_name, "public_url" : public_url})