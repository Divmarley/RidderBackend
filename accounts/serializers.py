import base64 
from rest_framework import serializers
from .models import *
from django.core.files.base import ContentFile


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
    
class UserSerializer(serializers.ModelSerializer):
    """add later 
    'is_verified'

    """
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone', 'name', 'account_type','is_active','thumbnail','push_token']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
    
class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = ['id', 'user', 'license_number', 'vehicle_registration_number', 'vehicle_model', 'vehicle_color', 'available', 'completed_trips','access_token']

class RiderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiderProfile
        fields = ['id', 'user', 'payment_method', 'preferred_driver_rating','access_token']

class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, default=" ")

    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'name', 'password', 'account_type','is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if not attrs.get('email') and not attrs.get('phone'):
            raise serializers.ValidationError("Either email or phone is required.")
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data.get('email'),
            phone=validated_data.get('phone'),
            name=validated_data.get('name'),  # Making name optional
            
            is_active=validated_data.get('is_active'),  # Making name optional
            password=validated_data['password'],
            account_type=validated_data['account_type']
        )
        user.generate_verification_code()
        # if user.account_type == 'driver':
        #     DriverProfile.objects.create(user=user.id)
        
        return user
    
class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()

class VerifyLoginSerializer(serializers.Serializer):
    # phone = serializers.CharField()
    email_or_phone = serializers.CharField()
    verification_code = serializers.CharField(max_length=4)

class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = Base64ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['profile_picture']

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'name', 'password', 'account_type']

class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInfo
        fields = ['id', 'driver', 'name', 'email', 'phone', 'address']

class VehicleInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleInfo
        fields = ['id', 'driver', 'model', 'color', 'year', 'vehicle_registration_number', 'vehicle_license_number']

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'driver', 'driver_photo', 'document_type', 'proof_of_insurance', 'roadworthiness', 'identification_card', 'document_file']

class UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        fields = ['id', 'driver', 'upload_file']


class CreateAllDataSerializer(serializers.Serializer):
    personal_info = PersonalInfoSerializer()
    vehicle_info = VehicleInfoSerializer()
    documents = DocumentSerializer(many=True)

    def create(self, validated_data):
        user = self.context['request'].user

        personal_info_data = validated_data.pop('personal_info')
        personal_info = PersonalInfo.objects.create(driver=user, **personal_info_data)

        vehicle_info_data = validated_data.pop('vehicle_info')
        vehicle_info = VehicleInfo.objects.create(driver=user, **vehicle_info_data)

        documents_data = validated_data.pop('documents')
        documents = [Document.objects.create(driver=user, **doc_data) for doc_data in documents_data]

        return {
            'personal_info': personal_info,
            'vehicle_info': vehicle_info,
            'documents': documents
        }