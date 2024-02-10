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

from werkzeug.security import check_password_hash
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from mahjong.utils import updater_info
from mahjong import models
from mahjong.web import forms
from .. import oauth

from . import paginations

module = Blueprint("submit_flags", __name__, url_prefix="/submit_flags")
bcrypt = Bcrypt()


@module.route("/", methods=["GET", "POST"])
@login_required
def index():
    submit_flags = models.FlagQuestion.objects()
    flag = request.args.get("flag")
    submit_flag_id = request.args.get("submit_flag_id")

    if flag and submit_flag_id:
        return redirect(
            url_for(
                "submit_flags.submit_flag_question",
                submit_flag_id=submit_flag_id,
                flag=flag,
            )
        )

    if flag and submit_flag_id:
        return redirect(
            url_for(
                "submit_flags.submit_flag_question",
                flag=flag,
                submit_flag_id=submit_flag_id,
            )
        )
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


@module.route("<submit_flag_id>/download_file", methods=["GET", "POST"])
def download(submit_flag_id):
    submit_flag = models.FlagQuestion.objects(id=submit_flag_id)
    try:
        submit_flag = models.FlagQuestion.objects(id=submit_flag_id).first()
    except:
        return abort(404)

    res = send_file(
        submit_flag.upload_file,
        download_name=submit_flag.upload_file.filename,
        mimetype=submit_flag.upload_file.content_type,
    )
    return res


@module.route("<submit_flag_id>/submit_flag/<flag>", methods=["GET", "POST"])
def submit_flag_question(submit_flag_id, flag):
    try:
        submit_flag = models.FlagQuestion.objects.get(id=submit_flag_id)
    except:
        return redirect(url_for("submit_flags.index"))

    if check_password_hash(submit_flag.flag, flag):
        current_user.score += submit_flag.point
        submit_flag.problem_solvers.append(current_user.team)

    submit_flag.save()
    current_user.save()
    return redirect(url_for("submit_flags.index"))
