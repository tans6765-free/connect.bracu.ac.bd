# Google OAuth Setup Guide
# ========================

## For Local Development

### 1. Get Google OAuth Credentials
1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Go to "Credentials" 
4. Click "Create Credentials" → "OAuth 2.0 Client IDs"
5. Choose "Web Application"
6. Add Authorized JavaScript origins:
   - http://localhost:8000
   - http://127.0.0.1:8000

7. Add Authorized redirect URIs:
   - http://localhost:8000/accounts/google/login/callback/

8. Copy your Client ID and Client Secret

### 2. Set Environment Variables

**Option A: Using .env file (Recommended)**
Create a `.env` file in the project root:
```
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
SECRET_KEY=your-secret-key-here
DEBUG=True
```

Then load it before running the server:
```powershell
# On Windows PowerShell
if (Test-Path .env) {
  Get-Content .env | ForEach-Object {
    $parts = $_ -split '=', 2
    if ($parts.Count -eq 2) {
      [Environment]::SetEnvironmentVariable($parts[0], $parts[1], "Process")
    }
  }
}
python manage.py runserver
```

**Option B: Direct Environment Variables (PowerShell)**
```powershell
$env:GOOGLE_CLIENT_ID = "your-client-id"
$env:GOOGLE_CLIENT_SECRET = "your-client-secret"
$env:SECRET_KEY = "your-secret-key"
python manage.py runserver
```

## For Vercel Deployment

### Add Environment Variables in Vercel

1. Go to your Vercel project dashboard
2. Go to Settings → Environment Variables
3. Add:
   - Key: `GOOGLE_CLIENT_ID`, Value: your-client-id
   - Key: `GOOGLE_CLIENT_SECRET`, Value: your-client-secret
   - Key: `SECRET_KEY`, Value: your-django-secret-key

4. Add Authorized redirect URIs in Google Cloud:
   - https://yourdomain.vercel.app/accounts/google/login/callback/
   - https://yourdomain.com/accounts/google/login/callback/ (if using custom domain)

5. Redeploy on Vercel

## Testing Google Sign-In

1. With credentials set, the login page will show an enabled "Google" button
2. Click it to start Google OAuth flow
3. You'll be redirected to Google login
4. After authentication, you'll be redirected back to the app

## Troubleshooting

**"Missing required parameter: client_id"**
- Credentials not set in environment variables
- Check that GOOGLE_CLIENT_ID is properly set

**"Redirect URI mismatch"**
- The URI in Google Console doesn't match your app's URI
- Make sure redirect URI matches exactly (including http/https)

**"Access blocked"**
- Verify the app is added to Google Cloud Console
- Check that Google+ API is enabled

## Local Testing Without Google OAuth

The app works perfectly fine without Google credentials:
- Login page displays with "Google (Not Configured)" button (disabled)
- Users can still log in with username/password
- Perfect for development without external dependencies
