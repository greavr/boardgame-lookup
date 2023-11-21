# Function to upload file to GCS and store record in Firestore

Designed for use in cloud function
Requires:
- GCS bucket with public access by default configured
- Firestore setup
- Cloud Function with permission to write to both

## Run Code Locally
```bash
pip3 install virtualenv
python3 -m virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
export GCS_BUCKET=boardgameapp-files
functions-framework --target=hello_http
```

## Env Vairables:
**Required**:\
`GCS_BUCKET` - Target GCS bucket for uploads (not default) \
**Optional** \
`ALLOWED_FILE_TYPES` - ALlowed File Types for Upload: **Default** - 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'txt'

