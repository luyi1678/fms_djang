from turtle import title
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from cryptography.fernet import Fernet
from django.conf import settings
import base64, os
from django.dispatch import receiver

# Create your models here.
class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name


class Mould(models.Model):
    class Meta:
        verbose_name = 'Mould'
        verbose_name_plural = 'Moulds'

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    client = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class Material(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    grade = models.CharField(max_length=100, null=True, blank=True)
    lot_number = models.CharField(max_length=64, blank=True, null=True)
    manufacturer = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'
        unique_together = ('grade', 'manufacturer')

    def __str__(self):
        return self.name


class Machine(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=64, blank=True, null=True)
    brand = models.CharField(max_length=64, blank=True, null=True)
    origin = models.CharField(max_length=64, blank=True, null=True)
    tonnage = models.CharField(max_length=64, blank=True, null=True)
    seri_numer = models.CharField(max_length=64, blank=True, null=True)
    location = models.CharField(max_length=64, blank=True, null=True)
    asset_number = models.CharField(max_length=64, blank=True, null=True, unique=True)
    name = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        verbose_name = 'Machine'
        verbose_name_plural = 'Machines'
        unique_together = ('location', 'seri_numer',)

    # def save(self, *args, **kwargs):
    #     self.name = f"{self.seri_numer} {self.location}"
    #     super(Machine, self).save(*args, **kwargs)

    def __str__(self):
        # return f"{self.name}"
        return f"{self.location}+{self.seri_numer}+{self.brand}+{self.tonnage}"



class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    # file_path = models.FileField(upload_to='uploads/',blank=True, null=True)
    file_path = models.FileField(blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)
    mould = models.ForeignKey(
        Mould, on_delete=models.SET_NULL, null=True, blank=True)
    machine = models.ForeignKey(
        Machine, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(blank=True, null=True)
    material = models.ForeignKey(Material,on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username + '-' + self.title

    def get_share_url(self):
        fernet = Fernet(settings.ID_ENCRYPTION_KEY)
        value = fernet.encrypt(str(self.pk).encode())
        value = base64.urlsafe_b64encode(value).decode()
        return reverse("share-file-id", kwargs={"id": (value)})

@receiver(models.signals.post_delete, sender=Post)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file_path:
        if os.path.isfile(instance.file_path.path):
            os.remove(instance.file_path.path)

@receiver(models.signals.pre_save, sender=Post)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).file_path
    except sender.DoesNotExist:
        return False

    new_file = instance.file_path
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class Process(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

