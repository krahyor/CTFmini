from flask_mongoengine.wtf import model_form
from flask_wtf import FlaskForm, file
from wtforms import fields, widgets, validators


from mahjong import models

BaseTeamsForm = model_form(
    models.Teams,
    FlaskForm,
    exclude=["created_by", "created_date", "last_updated_by", "updated_date", "score"],
    field_args={"name": {"label": "Name"}, "status": {"label": "Status"}},
)


class TeamsForm(BaseTeamsForm):
    pass
