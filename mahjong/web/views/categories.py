import datetime
import mongoengine as me
from . import paginations


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
from mahjong.utils import updater_info
from mongoengine.queryset.visitor import Q

module = Blueprint("categories", __name__, url_prefix="/categories")


@module.route("/")
@login_required
def index():
    categories = models.Category.objects(status="active")
    search_category = request.args.get("category", None)
    search_create_by = request.args.get("create_by", None)
    search_start_date = request.args.get("start_date", None)
    search_end_date = request.args.get("end_date", None)
    start_date = None
    end_date = None
    if search_start_date:
        start_date = datetime.datetime.strptime(search_start_date, "%d/%m/%Y")
    if search_end_date:
        end_date = datetime.datetime.strptime(search_end_date, "%d/%m/%Y")
    is_search = False

    if search_category:
        if categories:
            categories = categories.filter(name__icontains=search_category)
        is_search

    if search_create_by:
        if categories:
            create_by = models.User.objects(Q(first_name__icontains=search_create_by))
            categories = categories(Q(created_by__in=create_by))
        elif not is_search:
            categories = models.Category.objects(status="active=")
        is_search = True

    if search_start_date and search_end_date:
        if categories:
            categories = categories(
                Q(created_date__gte=search_start_date)
                | Q(
                    created_date__lte=end_date
                    + datetime.timedelta(hours=23, minutes=59, seconds=59)
                )
            )
        elif not is_search:
            categories = models.categories.objects(status="active")
        is_search = True

    if search_start_date:
        if categories:
            categories = categories(Q(created_date__gte=start_date))
        elif not is_search:
            categories = models.categories.objects(status="active")
        is_search = True

    if search_end_date:
        if categories:
            categories = categories(
                Q(
                    created_date__lte=end_date
                    + datetime.timedelta(hours=23, minutes=59, seconds=59)
                )
            )
        elif not is_search:
            categories = models.categories.objects(status="active")
        is_search = True

    pagination = paginations.get_paginate(
        data=categories,
        items_per_page=25,
    )
    return render_template(
        "/categories/index.html", categories=pagination["data"], pagination=pagination
    )


@module.route(
    "/create",
    methods=["GET", "POST"],
    defaults={"category_id": None},
)
@module.route("/<category_id>/edit", methods=["GET", "POST"])
@login_required
def create_or_edit(category_id):
    form = forms.categories.CategoryForm()
    categories = models.Category.objects()

    if category_id:
        categories = models.Category.objects.get(id=category_id)
        form = forms.categories.CategoryForm(obj=categories)
        categories.update_info.append(
            updater_info.create_update_information(current_user, request, "updated")
        )

    if not form.validate_on_submit():
        return render_template(
            "/categories/create-edit.html",
            form=form,
            categories=categories,
        )

    if not category_id:
        categories = models.Category(
            created_by=current_user._get_current_object(),
            last_updated_by=current_user._get_current_object(),
        )
        categories.update_info.append(
            updater_info.create_update_information(current_user, request, "created")
        )

    form.populate_obj(categories)
    categories.last_updated_by = current_user._get_current_object()
    categories.save()
    return redirect(
        url_for("categories.index"),
    )


@module.route("/<category_id>/delete", methods=["GET", "POST"])
@login_required
def delete(category_id):
    categories = models.Category.objects.get(id=category_id)
    categories.status = "disactive"
    categories.update_info.append(
        updater_info.create_update_information(current_user, request, "deleted")
    )
    categories.save()
    return redirect(
        url_for("categories.index"),
    )
