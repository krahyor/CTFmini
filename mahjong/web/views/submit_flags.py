import datetime
import mongoengine as me
import os
from mongoengine.queryset.visitor import Q

from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    session,
    redirect,
    send_file,
    abort,
)

from flask_login import login_user, logout_user, login_required, current_user
from mahjong.utils import updater_info
from mahjong import models
from mahjong.web import forms
from .. import oauth

from . import paginations

module = Blueprint("submit_flags", __name__, url_prefix="/submit_flags")


@module.route("/", methods=["GET", "POST"])
@login_required
def index():
    submit_flags = models.SubmitFlags.objects()

    # pagination = paginations.get_paginate(
    # data=upload_data,
    # items_per_page=25,
    # )

    return render_template(
        "submit_flags/index.html",
        submit_flags=submit_flags,
        # data_status=data_status,
        # catagory_data=catagory_data,
        # upload_data=pagination["data"],
        # pagination=pagination,
    )
