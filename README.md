# Secure Drive

## Overview

This project is a minimal backend for a security-focused “Google Drive knockoff”. It currently supports:

- Uploading a file (raw bytes) as an object into an S3-compatible object store (MinIO).
- Storing file metadata in PostgreSQL (not the file bytes).
- Downloading the file by streaming the object back to the client.

Authentication/Authorization/Accounting (AAA) is intentionally NOT implemented yet. The API temporarily takes `user_id` as a request field.

## What runs (processes) and their jobs

In a typical single Linux machine setup, these processes/services run:

1. FastAPI app (Python, run by Uvicorn)

   - Exposes HTTP API endpoints (upload/download).
   - Computes SHA-256 and size for uploaded files.
   - Writes object bytes to MinIO.
   - Writes/reads metadata rows in PostgreSQL.
   - Streams downloads from MinIO to the client.

2. PostgreSQL (database server)

   - Stores metadata only (object_id, user_id, object_key, content_type, size, sha256, timestamps, etc.).
   - Does NOT store file bytes.

3. MinIO (object storage server)
   - Stores the actual uploaded bytes as objects.
   - Objects are addressed by an object key (optionally `user_id/uuid` format).

So: 3 main processes/services (Uvicorn/FastAPI + Postgres + MinIO).

## API endpoints (current)

Base path: /api

1. POST /api/objects
   Purpose:

   - Upload a file (multipart/form-data) and store it as an object in MinIO.
   - Store metadata in PostgreSQL.

   Form fields:

   - user_id: string (temporary until AAA exists)
   - logical_name: optional string (display name)
   - file: actual uploaded file

   Returns JSON:

   - object_id (UUID string)
   - user_id
   - object_key (key inside MinIO)
   - name, content_type, size_bytes, sha256

2. GET /api/objects/{object_id}
   Purpose:

   - Download/stream the object bytes back to the client.

   Behavior:

   - Looks up metadata in PostgreSQL by object_id.
   - Fetches object from MinIO and streams it to the HTTP response.

## Environment variables

Backend reads configuration from environment variables:

PostgreSQL:

- DATABASE_URL
  Default used by code:
  postgresql+psycopg://postgres:postgres@localhost:5432/drive

MinIO:

- MINIO_ENDPOINT (default: localhost:9000)
- MINIO_ACCESS_KEY (default: minioadmin)
- MINIO_SECRET_KEY (default: minioadmin)
- MINIO_BUCKET (default: drive-objects)
- MINIO_SECURE (default: "0" for HTTP, "1" for HTTPS)

## How to run (Linux dev)

Prereqs:

- Python 3.10+ recommended
- A running PostgreSQL instance
- A running MinIO instance (local binary or Docker)

Step 1 — Start PostgreSQL

- Ensure a database named `drive` exists.
- Ensure the username/password in DATABASE_URL are correct.

Step 2 — Start MinIO
If using Docker, typical ports are:

- 9000 for S3 API
- 9001 for MinIO console (web UI)
  Make sure MINIO_ENDPOINT points to the S3 port (usually :9000).

Step 3 — Install Python dependencies
From the backend folder:
pip install -r requirements.txt

Step 4 — Export env vars (example)

```bash
  export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/drive"
  export MINIO_ENDPOINT="localhost:9000"
  export MINIO_ACCESS_KEY="minioadmin"
  export MINIO_SECRET_KEY="minioadmin"
  export MINIO_BUCKET="drive-objects"
  export MINIO_SECURE="0"
```

Step 5 — Run the FastAPI server
From the backend folder (so imports resolve as a package):
``` bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

What happens on first run:

- Tables are created automatically from SQLAlchemy models (minimal approach).
- The MinIO bucket is created automatically if it does not exist.

## Quick test (curl)

Upload:
``` bash
curl -F "user_id=u1" -F "file=@/path/to/test.pdf" http://127.0.0.1:8000/api/objects
```

Download:
``` bash
curl -L -o out.bin http://127.0.0.1:8000/api/objects/<object_id>
```

## Current security notes (important)

- Data is NOT encrypted yet. Objects are stored as raw bytes in MinIO.
- AAA is not implemented; `user_id` is trusted input right now (insecure by design for this stage).
- Use this only for local development/testing.

## Next milestones (recommended)

1. Add encryption (envelope encryption):

   - Encrypt file bytes before uploading to MinIO.
   - Store encryption metadata (algorithm, nonce/header, wrapped DEK) in PostgreSQL.

2. Add AAA:

   - Replace `user_id` form field with an authenticated identity.
   - Enforce access control on download/list.

3. Add listing and “folders”:
   - List objects by `user_id/` prefix in MinIO and/or via metadata queries in PostgreSQL.

## Troubleshooting

- If uploads fail: check MinIO endpoint/keys and confirm bucket creation works.
- If DB fails: verify DATABASE_URL, database exists, and Postgres is reachable.
- If imports fail: run uvicorn from the backend directory using `uvicorn app.main:app ...`.

If you paste your exact folder tree and the command you run, the README can be tailored to match your actual paths (especially if you’re not using `backend/app/...`).
