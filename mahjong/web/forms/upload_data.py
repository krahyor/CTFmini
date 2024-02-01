from flask_mongoengine.wtf import model_form
from flask_wtf import FlaskForm, file
from wtforms import fields, widgets, validators


from mahjong import models

BaseUploadDataForm = model_form(
    models.Upload_data,
    FlaskForm,
    exclude=[
        "uploaded_date",
        "upload_by",
        "upload_file",
        "last_updated_by",
        "updated_date",
        "upload_file_name",
    ],
    field_args={
        "name": {"label": "Name"},
        "description": {"label": "Description"},
        # "category": {"label": "Category", "label_modifier": lambda c: c.name},
    },
)


class UploadDataForm(BaseUploadDataForm):
    uploaded_file = file.FileField(
        "Excel File type (.xls or .xlsx)",
        validators=[
            file.FileAllowed(["xls", "xlsx"], "You can use xls and xlsx"),
        ],
    )
    category_choices = fields.SelectField("Category")
