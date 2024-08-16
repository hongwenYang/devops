from django.db import models
import uuid, time
from datetime import datetime


class Asset(models.Model):
    asset_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=50)
    purchase_date = models.DateField()
    owner = models.ForeignKey('user_management.User', on_delete=models.CASCADE)
    created_at = models.BigIntegerField(editable=False)

    def save(self, *args, **kwargs):
        if not self.created_at:
            # 获取当前时间的Unix时间戳，并存储到created_at字段中
            self.created_at = int(time.mktime(datetime.now().timetuple()))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
