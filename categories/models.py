from django.db import models
from django.urls import reverse

from users.models import User


class Category(models.Model):
    """
    Category model
    """
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, related_name="categories", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "categories"
