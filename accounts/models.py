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
    if not filename:
        filename = f'default_thumbnail.jpg'  # Provide a default filename
    extension = filename.split('.')[-1]
    return f'thumbnails/{instance.phone}.{extension}'


class CustomUser(AbstractBaseUser,PermissionsMixin):
    ACCOUNT_TYPE_CHOICES = [
        ('driver', 'Driver'),
        ('rider', 'Rider'),
        ('repair', 'Repair'),
        ('user', 'User'),
        ('restaurant', 'Restaurant'),
        ('pharmacy','Pharmacy'),
    ]

    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15,  null=True, blank=True)
    name = models.CharField(max_length=255)
    email_phone = models.CharField(max_length=255, null=True, blank=True)  # Optional field for email or phone  
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
    REQUIRED_FIELDS = ['name', 'account_type','is_aproved']

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

class RepairProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    class Meta:
        db_table = 'Repair Profile'
        managed = True
        verbose_name = 'Repair Profile'
        verbose_name_plural = 'Repair Profiles'

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
    class Meta:
        db_table = 'Driver Profile'
        managed = True
        verbose_name = 'Driver Profile'
        verbose_name_plural = 'Driver Profile'

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
    
    class Meta:
        db_table = 'Rider Profile'
        managed = True
        verbose_name = 'Rider Profile'
        verbose_name_plural = 'Riders Profile'

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

    class Meta:
        db_table = 'Restaurant Profile'
        managed = True
        verbose_name = 'Restaurant Profile'
        verbose_name_plural = 'Restaurants Profile'

class PharmacyProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='pharmacy_profile')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    preferred_pharmacy_rating = models.FloatField(default=0)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.name} - Pharmacy Profile"
    
    def update_profile_picture_from_base64(self, base64_data):
        if base64_data:
            format, imgstr = base64_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{self.user.id}.{ext}')
            self.profile_picture = data
            self.save()

    class Meta:
        db_table = 'Pharmacy Profile'
        managed = True
        verbose_name = 'Pharmacy Profile'
        verbose_name_plural = 'Pharmacys Profile'

@receiver(post_save, sender=CustomUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        if instance.account_type == 'driver':
            profile = DriverProfile.objects.create(driver=instance)
        elif instance.account_type == 'user':
            profile = RiderProfile.objects.create(user=instance)
        elif instance.account_type == 'restaurant':
            profile = RestaurantProfile.objects.create(user=instance)
        elif instance.account_type == 'repair':
            profile = RepairProfile.objects.create(user=instance)
        elif instance.account_type == 'pharmacy':
            profile = PharmacyProfile.objects.create(user=instance)
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


    class Meta:
        db_table = 'Personal Information'
        managed = True
        verbose_name = 'Personal Information'
        verbose_name_plural = 'Personal Informations'

class VehicleInfo(models.Model):
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    vehicle_name = models.CharField(max_length=100,null=True, blank=True)
    model = models.CharField(max_length=100,null=True, blank=True)
    color = models.CharField(max_length=100,null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    vehicle_registration_number = models.CharField(max_length=50,null=True, blank=True)
    vehicle_license_number = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'Vehicle Information'
        managed = True
        verbose_name = 'Vehicle Information'
        verbose_name_plural = 'Vehicle Informations'

class Document(models.Model):
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50, null=True, blank=True)  # e.g. 'driver_photo', 'proof_of_insurance', etc.
    document_file = models.FileField(upload_to='documents/', null=True, blank=True)

    class Meta:
        db_table = 'Document'
        managed = True
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

class Upload(models.Model):
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    upload_file = models.FileField(upload_to='uploads/',null=True, blank=True)
    
    class Meta:
        db_table = 'Upload'
        managed = True
        verbose_name = 'Upload'
        verbose_name_plural = 'Uploads'



class APKUpload(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    apk_file = models.FileField(upload_to='apks/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} v{self.version}"