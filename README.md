# BRAC Student Portal Clone

This repository contains a Python web application that replicates the BRAC student portal UI from the screenshots.

## Features
- Google OAuth login using the provided credentials
- Only `md.tahsinul.islam@g.bracu.ac.bd` can access the portal
- Page routes that match screenshot URLs
- Responsive side navigation and portal-style dashboard layout
- Deployment-ready for Vercel with `vercel.json`

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and add your environment variables.
3. Run locally:
   ```bash
   python app.py
   ```
4. Visit `http://127.0.0.1:8000/student/dashboard`.

## Vercel Deployment
- Vercel will use `app.py` as the Python entrypoint.
- Keep `vercel.json` and `requirements.txt` in the repository.
- Add the environment variables to Vercel:
  - `SECRET_KEY`
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
- Set the following Google OAuth redirect URIs in Google Cloud Console:
  - `http://localhost:8080/accounts/google/login/callback/`
  - `https://connectbracuacbd.vercel.app/accounts/google/login/callback/`
  - `https://connectbracuacbd.vercel.app`
- The login page is served at `/` and `/accounts/google/login/`.
- The OAuth authorization redirect route is `/accounts/google/auth/`.

## Assets
Place the following files in the `static` directory:
- `favicon.ico` — site icon
- `brac-logo.svg` — BRAC university logo
- `bracit.svg` — BRAC IT logo
- `grade_sheet.pdf` — grade sheet document

The app already includes placeholder images and a sample PDF for local testing.
