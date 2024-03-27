import mongoengine as me
import datetime


class Teams(me.Document):
    name = me.StringField(required=True, unique=True, max_length=50)
    status = me.StringField(default="active")
    created_by = me.ReferenceField("User", dbref=True, require=True)
    created_date = me.DateTimeField(required=True, default=datetime.datetime.now)
    last_updated_by = me.ReferenceField("User", dbref=True, require=True)
    updated_date = me.DateTimeField(
        required=True, default=datetime.datetime.now, auto_now=True
    )
    score = me.IntField()
    meta = {"collection": "teams"}
