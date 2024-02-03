import mongoengine as me
import datetime
from .updates import UpdateInformation


class SubmitFlags(me.Document):

    problem_header = me.StringField(required=True, max_length=256)  # หัวข้อโจทย์
    description = me.StringField()  # รายละเอียด
    category = me.ReferenceField("Category", dbref=True)  # หมวดหมู่
    status = me.StringField(default="failled")
    upload_file = me.FileField(required=True)
    upload_file_name = me.StringField(required=True, default="")

    problem_solvers = me.ListField(default=[])
    hint = me.StringField(default="", max_length=512)
    flag = me.StringField(required=True, default="", max_length=512)
    point = me.IntField(required=True, default=50)

    # อัพเดตเวลา
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )
    last_updated_by = me.ReferenceField("User", dbref=True, required=True)
    uploaded_date = me.DateTimeField(required=True, default=datetime.datetime.now)

    # อัพโหลดโดย
    update_info = me.EmbeddedDocumentListField("UpdateInformation")
    upload_by = me.ReferenceField("User", dbref=True, required=True)

    meta = {"collection": "submitflags"}

    def get_uploaded_date(self):
        uploaded_datetime = self.uploaded_date.date().strftime("%d/%m/%Y")
        return uploaded_datetime
