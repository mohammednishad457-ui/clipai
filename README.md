# ClipAI — starter project

This repository contains a public-facing UI preview and a local FastAPI backend starter.

## Contents
- `frontend/index.html` — ClipAI landing/upload interface
- `frontend/admin.html` — non-secure admin dashboard preview (do not use for real administration)
- `backend/main.py` — upload API and FFmpeg sample clip generation
- `backend/requirements.txt` — Python dependencies

## Important limitations
This is an early development starter, not a production AI clipping service. The backend currently creates up to three evenly spaced sample clips; it does not detect semantic highlights, generate captions, provide accounts, or persist jobs across restarts. YouTube URL downloading is not implemented. Only process videos you own or have permission to edit.

## Run backend locally (Windows)
1. Install Python 3.12 and FFmpeg, including `ffprobe`, and ensure both are on PATH.
2. Open a terminal in the `backend` folder.
3. Run `python -m venv .venv`
4. Run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
5. Run `.\.venv\Scripts\python.exe -m uvicorn main:app --reload`
6. Open `http://127.0.0.1:8000/docs`

Before public launch, add secure authentication, database, job queue, object storage, rate limits, file validation/scanning, HTTPS, restricted CORS, and secure admin authorization. Never put API keys or passwords in frontend code or this public repository.
