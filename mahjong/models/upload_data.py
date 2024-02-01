import mongoengine as me
import datetime
from .updates import UpdateInformation


class Upload_data(me.Document):
    meta = {"collection": "csv_uploads"}

    name = me.StringField(required=True, max_length=256)
    description = me.StringField()
    category = me.ReferenceField("Category", dbref=True)
    upload_by = me.ReferenceField("User", dbref=True, required=True)
    data_status = me.StringField(default="waiting")
    status = me.StringField(default="active")

    upload_file = me.FileField(required=True)
    upload_file_name = me.StringField(required=True, default="")
    last_updated_by = me.ReferenceField("User", dbref=True, required=True)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )
    uploaded_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    update_info = me.EmbeddedDocumentListField("UpdateInformation")

    def get_uploaded_date(self):
        uploaded_datetime = self.uploaded_date.date().strftime("%d/%m/%Y")
        return uploaded_datetime
