# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class TImgaeInfo(models.Model):
    id = models.BigIntegerField(primary_key=True)
    img_id = models.CharField(unique=True, max_length=10)
    location = models.CharField(max_length=128)
    description = models.CharField(max_length=128, blank=True, null=True)
    user_name = models.CharField(max_length=30)
    mtime = models.DateTimeField(auto_now=True)
    ctime = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 't_imgae_info'

class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username