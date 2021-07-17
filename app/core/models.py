import uuid
import os

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin

from django.conf import settings    # recommended way to import settings in django

def synthesize_image_file_path(instance, main_filename):
    """return a valid path for uploaded file with unique name"""
    main_file_extension = main_filename.split('.')[-1]
    new_filename = f'{uuid.uuid4()}.{main_file_extension}'

    return os.path.join('uploads/synthesize/', new_filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """ Creates and saves a new user"""
        if not email:
            raise ValueError('Users need to pass an valid email address!')

        user = self.model(email=self.normalize_email(email), **extra_fields) # not using password here cause
                                                        # password needs to be hashed and 
                                                        # not saved in clear text

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """ Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model that supports Creating a user using email in stead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"


class Tag(models.Model):
    """Model for tag management for Synthesize"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """String reprensation of tag object"""
        return self.name


class Chemcomp(models.Model):
    """Model for chemical components of synthesizer"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return self.name


class Synthesize(models.Model):
    """Model for declaring a synthesize for life"""
    title = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    time_years = models.IntegerField()
    link = models.CharField(blank=True, max_length=255)
    chemcomps = models.ManyToManyField('Chemcomp')
    tags = models.ManyToManyField('Tag')
    chance = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(null=True, upload_to=synthesize_image_file_path)

    def __str__(self) -> str:
        return self.title