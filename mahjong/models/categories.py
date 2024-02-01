import mongoengine as me
import datetime
from .updates import UpdateInformation


class Category(me.Document):
    meta = {"collection": "categories"}

    name = me.StringField(required=True, unique=True, max_length=50)
    status = me.StringField(default="active")
    created_by = me.ReferenceField("User", dbref=True, require=True)
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    last_updated_by = me.ReferenceField("User", dbref=True, require=True)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )
    update_info = me.EmbeddedDocumentListField("UpdateInformation")

    def get_created_date(self):
        created_date = self.created_date.date().strftime("%d/%m/%Y")
        return created_date
