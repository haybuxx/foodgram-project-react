from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7, null=True)
    slug = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name
