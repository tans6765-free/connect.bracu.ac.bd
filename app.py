import os
import traceback
from functools import wraps

from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.secret_key = os.getenv("SECRET_KEY", "django-insecure-dev-key-change-in-prod")
app.config["PREFERRED_URL_SCHEME"] = os.getenv("PREFERRED_URL_SCHEME", "https")

ALLOWED_EMAIL = "md.tahsinul.islam@g.bracu.ac.bd"
REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "https://connectbracuacbd.vercel.app/accounts/google/login/callback/",
)

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v2/",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    client_kwargs={"scope": "openid email profile"},
)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


@app.route("/")
def root():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return render_template(
        "login.html",
        page_title="Login | BRAC Student Portal",
        auth_route="/accounts/google/auth/",
    )


@app.route("/login")
@app.route("/accounts/google/login/")
def login():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return render_template(
        "login.html",
        page_title="Google Login | BRAC Student Portal",
        auth_route="/accounts/google/auth/",
    )


def get_google_env_status():
    missing = []
    if not google.client_id:
        missing.append("GOOGLE_CLIENT_ID")
    if not google.client_secret:
        missing.append("GOOGLE_CLIENT_SECRET")
    return missing


def ensure_trailing_slash(url: str) -> str:
    return url if url.endswith("/") else f"{url}/"


@app.route("/accounts/google/auth/")
def google_auth():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    redirect_uri = ensure_trailing_slash(REDIRECT_URI or url_for("auth_callback", _external=True))
    missing_env = get_google_env_status()
    if missing_env:
        return (
            "<h1>Google OAuth configuration error</h1>"
            f"<p>Missing environment variables: {', '.join(missing_env)}</p>"
            "<p>Please set them in Vercel or your local .env.</p>"
        ), 500

    try:
        return google.authorize_redirect(redirect_uri)
    except Exception:
        error_text = traceback.format_exc()
        return (
            "<h1>OAuth redirect failed</h1>"
            f"<p><strong>redirect_uri</strong>: {redirect_uri}</p>"
            f"<pre>{error_text}</pre>"
        ), 500


@app.route("/debug/redirect-uri")
def debug_redirect_uri():
    computed_uri = url_for("auth_callback", _external=True)
    env_status = get_google_env_status()
    env_message = (
        "All required Google env vars are present."
        if not env_status
        else f"Missing: {', '.join(env_status)}"
    )
    return (
        f"Computed callback URI: {computed_uri}<br>"
        f"Configured redirect URI: {ensure_trailing_slash(REDIRECT_URI)}<br>"
        f"Google env status: {env_message}"
    )


@app.route("/accounts/google/login/callback/")
def auth_callback():
    try:
        token = google.authorize_access_token()
        user_info = None
        if token and token.get("id_token"):
            user_info = google.parse_id_token(token)
        if not user_info:
            user_info = google.get("userinfo").json()

        email = user_info.get("email")
        if email != ALLOWED_EMAIL:
            return render_template(
                "unauthorized.html",
                email=email,
                allowed_email=ALLOWED_EMAIL,
            )
        session["user"] = {
            "name": user_info.get("name", "Student"),
            "email": email,
            "picture": user_info.get("picture", ""),
            "student_id": "22241090",
            "department": "DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING",
            "program": "BACHELOR OF SCIENCE IN COMPUTER SCIENCE",
            "current_semester": "FALL 2025",
            "cgpa": "2.36",
            "earned_credit": "63",
        }
        return redirect(url_for("dashboard"))
    except Exception:
        error_text = traceback.format_exc()
        return (
            "<h1>OAuth callback failed</h1>"
            f"<pre>{error_text}</pre>"
        ), 500


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("root"))


@app.route("/student/dashboard")
@login_required
def dashboard():
    return render_template("page.html", page="dashboard", user=session["user"])


@app.route("/student/advising/wish-list")
@login_required
def wish_list():
    return render_template("page.html", page="wish-list", user=session["user"])


@app.route("/student/advising/phase-one")
@login_required
def phase_one():
    return render_template("page.html", page="phase-one", user=session["user"])


@app.route("/student/advising/phase-two")
@login_required
def phase_two():
    return render_template("page.html", page="phase-two", user=session["user"])


@app.route("/student/advising/self-registration")
@login_required
def self_registration():
    return render_template("page.html", page="self-registration", user=session["user"])


@app.route("/student/advising/section-status")
@login_required
def section_status():
    return render_template("page.html", page="section-status", user=session["user"])


@app.route("/student/schedule")
@login_required
def schedule():
    return render_template("page.html", page="schedule", user=session["user"])


@app.route("/student/student-concession-apply")
@login_required
def concession_apply():
    return render_template("page.html", page="student-concession-apply", user=session["user"])


@app.route("/student/concession-history-list")
@login_required
def concession_history():
    return render_template("page.html", page="concession-history-list", user=session["user"])


@app.route("/student/course-drop-application")
@login_required
def course_drop():
    return render_template("page.html", page="course-drop-application", user=session["user"])


@app.route("/student/drop-semester-application")
@login_required
def drop_semester():
    return render_template("page.html", page="drop-semester-application", user=session["user"])


@app.route("/student/grade-sheet")
@login_required
def grade_sheet():
    return render_template("page.html", page="grade-sheet", user=session["user"])


@app.route("/student/probation-application")
@login_required
def probation():
    return render_template("page.html", page="probation-application", user=session["user"])


@app.route("/student/payslips")
@login_required
def payslips():
    return render_template("page.html", page="payslips", user=session["user"])


@app.route("/student/profile/overview")
@login_required
def profile_overview():
    return render_template("page.html", page="profile-overview", user=session["user"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)), debug=True)


application = app
