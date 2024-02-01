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
    amount_data = len(models.Upload_data.objects(status="active"))
    waiting_data = len(
        models.Upload_data.objects(status="active", data_status="waiting")
    )
    fail_data = len(models.Upload_data.objects(status="active", data_status="failed"))
    complete_data = len(
        models.Upload_data.objects(status="active", data_status="completed")
    )
    chart_data = [amount_data, waiting_data, fail_data, complete_data]
    sum_chart_data = sum(chart_data)
    return render_template(
        "dashboards/index.html",
        amount_data=amount_data,
        waiting_data=waiting_data,
        fail_data=fail_data,
        complete_data=complete_data,
        chart_data=chart_data,
        sum_chart_data=sum_chart_data,
    )
