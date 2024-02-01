import datetime
import mongoengine as me

from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    session,
    redirect,
)

from flask_login import login_user, logout_user, login_required, current_user

from mahjong import models
from mahjong.web import forms
from .. import oauth

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

module = Blueprint("accounts", __name__)


@module.route("/profile")
@login_required
def index():
    return render_template("accounts/index.html")


@module.route("/register", methods=["GET", "POST"])
def register():
    form = forms.accounts.RegistrationForm()
    if not form.validate_on_submit():
        return render_template("accounts/register.html", form=form)

    if oauth.create_user(form):
        return redirect(url_for("accounts.login"))
    return redirect(url_for("accounts.login", login_status="failed"))


@module.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboards.index"))

    form = forms.accounts.LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        user = models.User.objects(username=username).first()
        if user:
            if user.status == "unregistered" and oauth.handle_authorized_user(form):
                return redirect(url_for("accounts.setup_password", user_id=user.id))
            elif user.status == "disactive":
                messages = ["บัญชีถูกระงับ กรุณาติดต่อผู้ดูแลระบบ"]
                return render_template(
                    "/accounts/login.html", form=form, messages=messages
                )
            elif user and oauth.handle_authorized_user(form):
                return redirect(url_for("dashboards.index"))

            else:
                messages = ["Username หรือ Passwords ไม่ถูกต้องกรุณากรอกใหม่"]
                return render_template(
                    "/accounts/login.html", form=form, messages=messages
                )
        else:
            messages = ["Username หรือ Passwords ไม่ถูกต้องกรุณากรอกใหม่"]
            return render_template("/accounts/login.html", form=form, messages=messages)

    return render_template("accounts/login.html", form=form)


@module.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()

    return redirect(url_for("accounts.login"))


@module.route("/user/<user_id>/setup_password", methods=["GET", "POST"])
def setup_password(user_id):
    user = models.User.objects.get(id=user_id)
    form = forms.accounts.SetupPassword(obj=user)

    if not form.validate_on_submit():
        print(form.errors)
        return render_template("accounts/setup_password.html", form=form)

    password_hash = bcrypt.generate_password_hash(form.password.data)

    # Set the hashed password directly to the user's password field
    user.password = password_hash
    user.status = "active"
    user.save()

    return redirect(url_for("accounts.login"))


# @module.route("/login/<name>")
# def login_oauth(name):
#     client = oauth2.oauth2_client

#     scheme = request.environ.get("HTTP_X_FORWARDED_PROTO", "http")
#     redirect_uri = url_for(
#         "accounts.authorized_oauth", name=name, _external=True, _scheme=scheme
#     )
#     response = None
#     if name == "psu":
#         response = client.psu.authorize_redirect(redirect_uri)
#     elif name == "engpsu":
#         response = client.engpsu.authorize_redirect(redirect_uri)
#     return response

# @module.route("/auth/<name>")
# def authorized_oauth(name):
#     client = oauth2.oauth2_client
#     remote = None
#     try:
#         if name == "psu":
#             remote = client.psu
#         elif name == "engpsu":
#             remote = client.engpsu

#         token = remote.authorize_access_token()

#     except Exception as e:
#         print("autorize access error =>", e)
#         return redirect(url_for("accounts.login"))

#     session["oauth_provider"] = name
#     return oauth2.handle_authorized_oauth2(remote, token)

# @module.route("/logout")
# @login_required
# def logout():
#     name = session.get("oauth_provider")
#     logout_user()
#     session.clear()

#     client = oauth2.oauth2_client
#     remote = None
#     logout_url = None
#     if name == "psu":
#         remote = client.psu
#         logout_url = f"{ remote.server_metadata.get('end_session_endpoint') }?redirect={ request.scheme }://{ request.host }"
#     elif name == "engpsu":
#         remote = client.engpsu

#     if logout_url:
#         return redirect(logout_url)

#     return redirect(url_for("site.index"))
