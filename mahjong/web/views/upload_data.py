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

module = Blueprint("upload_data", __name__, url_prefix="/upload_data")


@module.route("/")
@login_required
def index():
    submit_flags = models.SubmitFlags.objects()
    return render_template("/upload_data/index.html", submit_flags=submit_flags)


@module.route(
    "/upload",
    methods=["GET", "POST"],
    defaults={"upload_data_id": None},
)
@module.route("/<upload_data_id>/edit", methods=["GET", "POST"])
@login_required
def create_or_edit(upload_data_id):
    upload_data = models.SubmitFlags.objects()
    form = forms.upload_data.UploadDataForm()
    categories = models.Category.objects(status="active")

    if upload_data_id:
        upload_data = models.SubmitFlags.objects.get(id=upload_data_id)
        form = forms.upload_data.UploadDataForm(obj=upload_data)
        upload_data.update_info.append(
            updater_info.create_update_information(current_user, request, "updated")
        )

    form.category.choices = [(i.id, i.name) for i in categories]
    if not form.validate_on_submit():
        print(form.errors)
        return render_template("/upload_data/create-edit.html", form=form)

    if not upload_data_id:
        upload_data = models.SubmitFlags(
            upload_by=current_user._get_current_object(),
            last_updated_by=current_user._get_current_object(),
        )
        upload_data.update_info.append(
            updater_info.create_update_information(current_user, request, "created")
        )

    form.populate_obj(upload_data)
    category = models.Category.objects(id=form.category.data).first()
    upload_data.category = category

    if not upload_data_id:
        if form.uploaded_file.data:
            upload_data.upload_file.put(
                form.uploaded_file.data,
                filename=form.uploaded_file.data.filename,
                content_type=form.uploaded_file.data.content_type,
            )
    else:
        if form.uploaded_file.data:
            upload_data.upload_file.replace(
                form.uploaded_file.data,
                filename=form.uploaded_file.data.filename,
                content_type=form.uploaded_file.data.content_type,
            )

    if form.uploaded_file.data:
        upload_data.upload_file_name = form.uploaded_file.data.filename
    upload_data.last_updated_by = current_user._get_current_object()
    upload_data.save()

    return redirect(url_for("upload_data.index"))


@module.route("<upload_data_id>/delete", methods=["GET", "POST"])
@login_required
def delete(upload_data_id):
    upload_data = models.Upload_data.objects.get(id=upload_data_id)
    upload_data.status = "disactive"
    upload_data.update_info.append(
        updater_info.create_update_information(current_user, request, "deleted")
    )
    upload_data.save()
    return redirect(url_for("upload_data.index"))


@module.route("<upload_data_id>/download_file", methods=["GET", "POST"])
def download(upload_data_id):
    upload_data = models.Upload_data.objects(id=upload_data_id)
    try:
        upload_data = models.Upload_data.objects(
            id=upload_data_id, status="active"
        ).first()
    except:
        return abort(404)

    res = send_file(
        upload_data.upload_file,
        download_name=upload_data.upload_file.filename,
        mimetype=upload_data.upload_file.content_type,
    )
    return res
