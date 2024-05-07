from uuid import uuid4

from django.contrib.gis.db import models


class Consumer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
