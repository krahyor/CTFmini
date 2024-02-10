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
from .. import forms
from .. import oauth

module = Blueprint("dashboards", __name__, url_prefix="/dashboard")


@module.route("/", methods=["GET", "POST"])
@login_required
def index():
    users = models.User.objects(roles=["user"]).order_by("-score")
    return render_template("dashboards/index.html", users=users)
