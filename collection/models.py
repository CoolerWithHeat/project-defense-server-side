import requests
from django.db import models
from django.core.files.base import ContentFile
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

authentication_options =  (
    ('Google', 'Google'),
    ('Facebook', 'Facebook'),
    ('Custom', 'Custom'),
    )

TOPIC_CHOICES = (
    ('Books', 'Books'),
    ('Post Stamps', 'Post Stamps'),
    ('Whiskeys', 'Whiskeys'),
    ('Other', 'Other'),
    )

FIELD_TYPES = (
        ('integer', 'Integer'),
        ('string', 'String'),
        ('text', 'Multiline Text'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
    )

def default_custom_fields():
    return {}


def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return ContentFile(response.content)
    return None


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user



class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    full_name = models.CharField(max_length=45, null=False, blank=False, default='Not Known')
    authenticated_by = models.CharField(choices=authentication_options, max_length=8, default=authentication_options[0][0])
    profile_image = models.FileField(default='itransition_logo.png', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

class CustomField(models.Model):

    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)



class Tag(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    

class Collection(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True, default=None)
    topic = models.CharField(choices=TOPIC_CHOICES, max_length=35, null=True, blank=True, default=None)
    image = models.FileField(default=None, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    custom_fields = models.JSONField(default=default_custom_fields, blank=True)
    
    def __str__(self):
        return self.name    
    
class Item(models.Model):
    collection = models.ForeignKey (Collection, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    tags = models.ManyToManyField(Tag, blank=True)
    additional_field_data = models.JSONField(default=default_custom_fields, blank=True, null=True)

    def __str__(self):
        return f'{self.name} of collection {self.collection.name} <==> {self.id}'

class Comment(models.Model):
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

class Like(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email