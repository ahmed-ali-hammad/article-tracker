from datetime import datetime
from zoneinfo import ZoneInfo

from marshmallow import Schema, fields
from src.db.models import ArticleDetail


class ArticleDetailSchema(Schema):
    id = fields.Int(data_key="article_detail_id")
    article_id = fields.Int()
    topline = fields.Str()
    headline = fields.Str()
    timestamp = fields.Method("get_german_timestamp", data_key="Dated")
    text = fields.Str()

    def get_german_timestamp(self, obj):
        utc_time = datetime.fromtimestamp(obj.timestamp, tz=ZoneInfo("UTC"))
        return utc_time.astimezone(ZoneInfo("Europe/Berlin")).isoformat()


class ArticleDetailIdOnlySchema(Schema):
    id = fields.Int(data_key="article_detail_id")


class ArticleSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Int()
    topline = fields.Str()
    headline = fields.Str()
    is_updated = fields.Method(
        "check_is_updated"
    )  # True if multiple crawls produced different versions of the article
    article_url = fields.Str()
    details = fields.Nested(ArticleDetailIdOnlySchema, many=True, data_key="versions")

    def check_is_updated(self, obj: ArticleDetail) -> bool:
        # Returns True if article has >1 detail, else False
        return len(obj.details) > 1
