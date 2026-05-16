# BRAC University Portal — Setup Guide

## Quick Start (Localhost)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up `.env` (already pre-filled)
The `.env` file already has your credentials. For localhost, `VERCEL_URL` is set to `localhost:8080`.

### 3. Load environment variables
```bash
# On Windows PowerShell:
Get-Content .env | ForEach-Object {
  if ($_ -match '^([^#][^=]*)=(.*)$') {
    [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
  }
}

# On Mac/Linux:
export $(grep -v '^#' .env | xargs)
```

### 4. Run migrations and setup Google OAuth
```bash
python manage.py migrate
python manage.py setup_google_oauth
```

### 5. Run the server
```bash
# Port 8080 matches the Google OAuth callback URL you registered
python manage.py runserver 8080
```

Open: http://localhost:8080

---

## Deploying to Vercel

### 1. Push to GitHub (see git commands below)

### 2. Vercel environment variables  
In your Vercel project → Settings → Environment Variables, add:
```
SECRET_KEY        = (a strong random string for production)
GOOGLE_CLIENT_ID  = <your-google-client-id>
GOOGLE_CLIENT_SECRET = <your-google-client-secret>
VERCEL_URL        = connectbracuacbd.vercel.app
```

`build.sh` runs automatically on every deploy and calls `setup_google_oauth` to configure OAuth from env vars.

---

## Google OAuth Callback URLs (already registered)
- `http://localhost:8080/accounts/google/login/callback/`
- `https://connectbracuacbd.vercel.app/accounts/google/login/callback/`

---

## Git Commands

### First time push:
```bash
git add -A
git commit -m "feat: rebuild portal UI to match connect.bracu.ac.bd"
git push origin main
```

### After any changes:
```bash
git add -A
git commit -m "your message here"
git push origin main
```

---

## How Google Login Works (No 3rd-party blockers)

The login page uses **`{% provider_login_url 'google' %}`** from django-allauth.  
This generates a **direct server-side redirect** to Google — no external JavaScript, no popup, no `accounts.google.com` scripts loaded on the page.

Flow:
1. User clicks "Continue with Google"
2. Browser navigates to `/accounts/google/login/` (your server)
3. Your server redirects to Google's OAuth page
4. Google redirects back to `/accounts/google/login/callback/`
5. Your server validates → logs in → redirects to dashboard

This means **ad blockers / privacy extensions cannot interfere** because there is no 3rd-party script.

---

## Troubleshooting

**Google button does nothing / 500 error:**
Visit `/health/` — it shows whether `GOOGLE_CLIENT_ID` is set and the SocialApp is configured.

**"Access denied" after Google login:**  
Only `md.tahsinul.islam@g.bracu.ac.bd` is whitelisted. The adapter in `portal/adapters.py` blocks all other emails.

**Localhost OAuth not working:**  
Make sure you're running on port `8080` (matches the registered callback URL).
