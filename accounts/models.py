import base64
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import random
import string
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.base import ContentFile
from django.contrib.auth.models import PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email=None, phone=None, password=None, account_type=None, **extra_fields):
        if not email and not phone:
            raise ValueError('The Email or Phone field must be set')
        email = self.normalize_email(email) if email else None
        user = self.model(email=email, phone=phone, account_type=account_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not email:
            raise ValueError('Superuser must have an email address')
        
        user = self.create_user(
            email=self.normalize_email(email), 
            phone=None, 
            password=password, 
            **extra_fields
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


def upload_thumbnail(instance, filename):
    
	path = f'thumbnails/{instance.phone}'
    
	extension = filename.split('.')[-1]
	if extension:
		path = path + '.' + extension
	return path


class CustomUser(AbstractBaseUser,PermissionsMixin):
    ACCOUNT_TYPE_CHOICES = [
        ('driver', 'Driver'),
        ('rider', 'Rider'),
        ('user', 'User'),
        ('restaurant', 'Restaurant'),
    ]

    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='rider')
    is_active = models.BooleanField(default=True)
    is_aproved = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=4, null=True, blank=True)
    push_token=  models.CharField(max_length=255, null=True, blank=True)
    thumbnail  = models.ImageField(
		upload_to=upload_thumbnail,
		null=True,
		blank=True
	)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'account_type']

    def save(self, *args, **kwargs):
        if not self.email and not self.phone:
            raise ValueError('The Email or Phone field must be set')
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()
        super().save(*args, **kwargs)

    def generate_verification_code(self):
        return ''.join(random.choices(string.digits, k=4))

    def __str__(self):
        return self.email if self.email else self.phone
    
    class Meta:
        db_table = 'User'
        managed = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    class Meta:
        db_table = 'Profile'
        managed = True
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def update_profile_picture_from_base64(self, base64_data):
        if base64_data:
            format, imgstr = base64_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{self.user.id}.{ext}')
            self.profile_picture = data
            self.save()

class DriverProfile(models.Model):
    driver = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='driver_profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    # license_number = models.CharField(max_length=50, unique=True)
    # vehicle_registration_number = models.CharField(max_length=50, unique=True)
    # vehicle_model = models.CharField(max_length=100)
    # vehicle_color = models.CharField(max_length=30)
    # available = models.BooleanField(default=True)
    # completed_trips = models.PositiveIntegerField(default=0)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.name} - Driver Profile"
    
    def update_profile_picture_from_base64(self, base64_data):
        if base64_data:
            format, imgstr = base64_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{self.user.id}.{ext}')
            self.profile_picture = data
            self.save()

class RiderProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='rider_profile')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    preferred_driver_rating = models.FloatField(default=0)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.name} - Rider Profile"
    
    def update_profile_picture_from_base64(self, base64_data):
        if base64_data:
            format, imgstr = base64_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{self.user.id}.{ext}')
            self.profile_picture = data
            self.save()



class RestaurantProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='restaurant_profile')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    preferred_driver_rating = models.FloatField(default=0)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.name} - Restaurant Profile"
    
    def update_profile_picture_from_base64(self, base64_data):
        if base64_data:
            format, imgstr = base64_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{self.user.id}.{ext}')
            self.profile_picture = data
            self.save()

@receiver(post_save, sender=CustomUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        if instance.account_type == 'driver':
            profile = DriverProfile.objects.create(driver=instance)
        elif instance.account_type == 'user':
            profile = RiderProfile.objects.create(user=instance)
        elif instance.account_type == 'restaurant':
            profile = RestaurantProfile.objects.create(user=instance)
        # else:
        #     profile = Profile.objects.create(user=instance)
        
        refresh = RefreshToken.for_user(instance)
        profile.access_token = str(refresh.access_token)
        profile.save()


    # @receiver(post_save, sender=CustomUser)
    # def create_auth_token(sender, instance=None, created=False, **kwargs):
    #     if created:
    #         DriverProfile.objects.create(user=instance)
    #         refresh = RefreshToken.for_user(instance)
    #         instance.profile.access_token = str(refresh.access_token)
    #         instance.profile.save()

class PersonalInfo(models.Model):
    driver = models.ForeignKey(CustomUser, related_name="driver_info", on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15,null=True, blank=True)
    address = models.TextField(null=True, blank=True)

class VehicleInfo(models.Model):
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    model = models.CharField(max_length=100,null=True, blank=True)
    color = models.CharField(max_length=100,null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    vehicle_registration_number = models.CharField(max_length=50,null=True, blank=True)
    vehicle_license_number = models.CharField(max_length=50, null=True, blank=True)

class Document(models.Model):
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    driver_photo = models.ImageField(upload_to='documents/',null=True, blank=True)
    document_type = models.CharField(max_length=50,null=True, blank=True)
    proof_of_insurance = models.ImageField(upload_to='documents/',null=True, blank=True)
    roadworthiness = models.ImageField(upload_to='documents/',null=True, blank=True)
    identification_card = models.ImageField(upload_to='documents/',null=True, blank=True)
    document_file = models.FileField(upload_to='documents/',null=True, blank=True)

class Upload(models.Model):
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    upload_file = models.FileField(upload_to='uploads/',null=True, blank=True)
    



