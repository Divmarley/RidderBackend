import base64 
from rest_framework import serializers
from .models import *
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from django.core.files.base import ContentFile
import base64
import six
import uuid
 
class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')
            # Decode the base64 string
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate a file name
            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension)
            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension
    
class PUserSerializer(serializers.ModelSerializer):
	name = serializers.SerializerMethodField()

	class Meta:
		model = CustomUser
		fields = [
			'phone',
			'name',
			'thumbnail'
		]

	def get_name(self, obj):
		fname = obj.first_name.capitalize()
		lname = obj.last_name.capitalize()
		return fname + ' ' + lname
    
class UserSerializer(serializers.ModelSerializer):
    """add later 
    'is_verified'

    """
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone', 'name', 'account_type','is_active','thumbnail','push_token','is_aproved']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
    

class RiderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiderProfile
        fields = ['id', 'user', 'payment_method', 'preferred_driver_rating','access_token']

from rest_framework import serializers
from .models import CustomUser
from django.core.exceptions import ValidationError

class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, default="")
    password = serializers.CharField(write_only=True, required=False)
    account_type = serializers.ChoiceField(choices=CustomUser.ACCOUNT_TYPE_CHOICES, required=False, default='rider')
    
    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'name', 'password', 'account_type', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')
        password = attrs.get('password')
        
        if not email and not phone:
            raise serializers.ValidationError("Either email or phone is required.")

        # If email is provided, require a password
        if email and not password:
            raise serializers.ValidationError("Password is required when email is provided.")

        # Sanitize phone
        if phone:
            import re
            phone_sanitized = re.sub(r'[^0-9]', '', phone)
            attrs['phone'] = phone_sanitized
            phone = phone_sanitized

        # Default account_type
        if not attrs.get('account_type'):
            attrs['account_type'] = 'rider'

        # Check if a user with the same email or phone exists
        email_phone = email if email else phone
        if CustomUser.objects.filter(email_phone=email_phone).exists():
            raise serializers.ValidationError("A user with this email or phone already exists.")

        return attrs

    def create(self, validated_data):
        email = validated_data.get('email')
        phone = validated_data.get('phone')
        name = validated_data.get('name', '')
        account_type = validated_data.get('account_type', 'rider')
        is_active = validated_data.get('is_active', True)
        password = validated_data.get('password')
        if not password:
            import secrets
            password = secrets.token_urlsafe(12)

        # Set email_phone automatically
        email_phone = email if email else phone

        user = CustomUser.objects.create_user(
            email=email,
            phone=phone,
            email_phone=email_phone,
            name=name,
            password=password,
            account_type=account_type,
            is_active=is_active
        )

        # Generate verification code
        user.verification_code = user.generate_verification_code()
        user.save()

        return user


import re 
class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate(self, attrs):
        phone = attrs.get("phone", "")
        email = attrs.get("email", "")
        print("Validating LoginSerializer with phone:", phone, "and email:", email)
        # Require at least one field
        if not phone and not email:
            raise serializers.ValidationError("Provide either phone or email.")

        # Sanitize phone if provided
        if phone:
            sanitized_phone = re.sub(r'[^0-9]', '', phone)  # keep only digits
            if len(sanitized_phone) > 20:
                raise serializers.ValidationError("Phone number is too long.")
            
            attrs["phone"] = sanitized_phone

        return attrs

    def create_group_name(self):
        """
        Group name should be based on sanitized phone OR email.
        """
        phone = self.validated_data.get("phone")
        email = self.validated_data.get("email")

        # Prefer phone → fallback to email
        return phone if phone else email


class VerifyLoginSerializer(serializers.Serializer):
    # phone = serializers.CharField()
    email_or_phone = serializers.CharField()
    verification_code = serializers.CharField(max_length=4)

class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = Base64ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['profile_picture','email', 'name']


class EditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','email', 'name']  # Include all fields or specify the ones needed
        read_only_fields = ['id']  # Ensure user field is not changed

    def update(self, instance, validated_data):
        """Handles updating the profile"""
        instance.name = validated_data.get('name', instance.name)
        instance.phone = validated_data.get('phone', instance.phone) 
        instance.save()
        return instance

    
class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'name', 'password', 'account_type']

class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInfo
        fields = ['id',  'name', 'email', 'phone', 'address']

class VehicleInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleInfo
        fields = ['id', 'vehicle_name', 'model', 'color', 'year', 'vehicle_registration_number', 'vehicle_license_number']

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id',   'document_type',  'document_file']

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import CustomUser, PersonalInfo, VehicleInfo, Document
# from .serializers import PersonalInfoSerializer, VehicleInfoSerializer, DocumentSerializer

class CreateAllDataSerializer(serializers.Serializer):
    documents = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=True
    )
    personal_info = PersonalInfoSerializer()
    vehicle_info = VehicleInfoSerializer()
    user_id = serializers.IntegerField()

    def create(self, validated_data):
        user_id = self.context.get('user_id')
        print("create user_id", user_id)

        user = CustomUser.objects.get(id=user_id)

        # Create PersonalInfo
        personal_info_data = validated_data.pop('personal_info')
        personal_info = PersonalInfo.objects.create(driver=user, **personal_info_data)

        # Create VehicleInfo
        vehicle_info_data = validated_data.pop('vehicle_info')
        vehicle_info = VehicleInfo.objects.create(driver=user, **vehicle_info_data)

        # Create Document instances for each uploaded file
        documents_data = validated_data.pop('documents')
        created_documents = []
        for file in documents_data: 
            doc = Document.objects.create(driver=user, document_file=file)
            created_documents.append(doc)

        return {
            'personal_info': PersonalInfoSerializer(personal_info).data,
            'vehicle_info': VehicleInfoSerializer(vehicle_info).data,
            'documents': DocumentSerializer(created_documents, many=True).data
        }
class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        fields = ['id', 'driver', 'upload_file']


class DriverProfileSerializer(serializers.ModelSerializer):
    driver =UserSerializer()
    # personal_info = PersonalInfoSerializer()
    # vehicle_info = VehicleInfoSerializer()
    # documents = DocumentSerializer(many=True)
    class Meta:
        model = DriverProfile
        fields = ['id', 'driver'] #'license_number', 'vehicle_registration_number', 'vehicle_model', 'vehicle_color', 'available', 'completed_trips','access_token'

class RiderProfileSerializer(serializers.ModelSerializer):
    user =UserSerializer()
    # personal_info = PersonalInfoSerializer()
    # vehicle_info = VehicleInfoSerializer()
    # documents = DocumentSerializer(many=True)
    class Meta:
        model = RiderProfile
        fields = ['id', 'user'] #'license_number', 'vehicle_registration_number', 'vehicle_model', 'vehicle_color', 'available', 'completed_trips','access_token'



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'phone']

    def validate_email(self, value):
        """Ensure email is valid and unique."""
        if CustomUser.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_phone(self, value):
        """Ensure phone number is valid and unique."""
        if CustomUser.objects.filter(phone=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return value
    


class APKUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = APKUpload
        fields = ['id', 'apk_file', 'version', ]


 

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
 

        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value
