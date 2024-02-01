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


@module.route("/", methods=["GET", "POST"])
@login_required
def index():
    upload_data = models.Upload_data.objects(status="active")
    catagory_data = models.Category.objects()
    search_name = request.args.get("name", None)
    search_category = request.args.get("category", None)
    search_file_name = request.args.get("file_name", None)
    search_status = request.args.get("status", None)
    search_start_date = request.args.get("start_date", None)
    search_end_date = request.args.get("end_date", None)
    start_date = None
    end_date = None
    if search_start_date:
        start_date = datetime.datetime.strptime(search_start_date, "%d/%m/%Y")
    if search_end_date:
        end_date = datetime.datetime.strptime(search_end_date, "%d/%m/%Y")

    data_status = [
        "waiting",
        "completed",
        "failed",
    ]
    is_search = False
    if search_name:
        if upload_data:
            upload_data = upload_data(Q(name__icontains=search_name))
        is_search = True

    if search_category:
        if upload_data:
            category = models.Category.objects(Q(name__icontains=search_category))
            upload_data = upload_data.filter(category__in=category)

        elif not is_search:
            upload_data = models.Upload_data.objects(status="active")
        is_search = True

    if search_file_name:
        if upload_data:
            upload_data = upload_data.filter(
                upload_file_name__icontains=search_file_name.lower()
            )
        elif not is_search:
            upload_data = models.Upload_data.objects(status="active")
        is_search = True

    if search_status:
        if upload_data:
            upload_data = upload_data.filter(
                data_status__icontains=search_status.lower()
            )
        elif not is_search:
            upload_data = models.Upload_data.objects(status="active")
        is_search = True

    if search_start_date and search_end_date:
        if upload_data:
            upload_data = upload_data(
                Q(uploaded_date__gte=search_start_date)
                | Q(
                    uploaded_date__lte=end_date
                    + datetime.timedelta(hours=23, minutes=59, seconds=59)
                )
            )
        elif not is_search:
            upload_data = models.Upload_data.objects(status="active")
        is_search = True

    if search_start_date:
        if upload_data:
            upload_data = upload_data(Q(uploaded_date__gte=start_date))
        elif not is_search:
            upload_data = models.Upload_data.objects(status="active")
        is_search = True

    if search_end_date:
        if upload_data:
            upload_data = upload_data(
                Q(
                    uploaded_date__lte=end_date
                    + datetime.timedelta(hours=23, minutes=59, seconds=59)
                )
            )
        elif not is_search:
            upload_data = models.Upload_data.objects(status="active")
        is_search = True

    pagination = paginations.get_paginate(
        data=upload_data,
        items_per_page=25,
    )

    return render_template(
        "upload_data/index.html",
        data_status=data_status,
        catagory_data=catagory_data,
        upload_data=pagination["data"],
        pagination=pagination,
    )


@module.route(
    "/upload",
    methods=["GET", "POST"],
    defaults={"upload_data_id": None},
)
@module.route("/<upload_data_id>/edit", methods=["GET", "POST"])
@login_required
def create_or_edit(upload_data_id):
    upload_data = models.Upload_data.objects()
    form = forms.upload_data.UploadDataForm()
    categories = models.Category.objects(status="active")

    if upload_data_id:
        upload_data = models.Upload_data.objects.get(id=upload_data_id)
        form = forms.upload_data.UploadDataForm(obj=upload_data)
        upload_data.update_info.append(
            updater_info.create_update_information(current_user, request, "updated")
        )

    form.category_choices.choices = [(i.id, i.name) for i in categories]
    if not form.validate_on_submit():
        print(form.errors)
        return render_template("/upload_data/create-edit.html", form=form)

    if not upload_data_id:
        upload_data = models.Upload_data(
            upload_by=current_user._get_current_object(),
            last_updated_by=current_user._get_current_object(),
        )
        upload_data.update_info.append(
            updater_info.create_update_information(current_user, request, "created")
        )

    form.populate_obj(upload_data)
    category = models.Category.objects(id=form.category_choices.data).first()
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
