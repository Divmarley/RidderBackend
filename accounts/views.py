from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.views.generic import ListView,View
from requests import request
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from accounts import send_verification_code
from chat.models import DriverOnline
from food.models import Image, Location, Rating, Restaurant
from .models import APKUpload, CustomUser, DriverProfile, PersonalInfo, RepairProfile, RiderProfile, Upload, VehicleInfo,Document
from .serializers import APKUploadSerializer, CreateAllDataSerializer, DocumentSerializer, DriverProfileSerializer, DriverSerializer, EditProfileSerializer, LoginSerializer, PersonalInfoSerializer, RegisterSerializer, RiderProfileSerializer, UploadSerializer, UserProfileSerializer, UserSerializer, VehicleInfoSerializer, VerifyLoginSerializer, ProfileSerializer
from .utils import send_verification_email



class HomeView(View):
    template_name = 'index.html'  # Replace with your actual template

    def get(self, request, *args, **kwargs):
        context = {
            # 'data': ...  # Add any data you want to pass to the template
        }
        return render(request, self.template_name, context)

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
 
class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()

                # Send verification email if user has email
                email_sent = False
                email_error = None
                if user.email:
                    email_sent, email_error = send_verification_email(user)

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                # Create DriverOnline instance if user is driver
                if user.account_type == 'driver':
                    DriverOnline.objects.create(
                        driver=user,
                        phone=user.phone,
                        location=request.data.get('location', ''),
                        latitude=request.data.get('latitude', 0.0),
                        longitude=request.data.get('longitude', 0.0),
                        push_token=request.data.get('push_token'),
                        ride_type=request.data.get('ride_type', 'Car')
                    )

                response_data = {
                    'detail': 'User created successfully',
                    'access_token': access_token,
                    'refresh_token': str(refresh),
                    'verification_code': user.verification_code,
                    'id': user.id
                }

                if user.email:
                    response_data['email_status'] = {
                        'sent': email_sent,
                        'error': email_error
                    }

                return Response(response_data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({
                    'detail': 'Registration failed',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TokenObtainView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        # Generate a refresh token without associating it with any user
        refresh = RefreshToken()
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })




class LoginAPIView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data.get("phone")
        email = serializer.validated_data.get("email")
        password = request.data.get("password")

        user = None

        # LOGIN WITH EMAIL
        if email:
            try:
                user = CustomUser.objects.get(email=email)
                print("User found with email:", user.password)
                email_sent, email_error = send_verification_email(user)
                print(' email_sent, email_error', email_sent, email_error)
            except CustomUser.DoesNotExist:
                return Response({"detail": "Email does not exist"}, status=404)

            if not password:
                return Response({"detail": "Password required for email login"}, status=400)

            if not user.check_password(password):
                return Response({"detail": "Invalid password"}, status=401)

        # LOGIN WITH PHONE
        elif phone:
            try:
                user = CustomUser.objects.get(phone=phone)
            except CustomUser.DoesNotExist:
                return Response({"detail": "Phone does not exist"}, status=404)

            # Phone-only auto-login
            if password:
                if not user.check_password(password):
                    return Response({"detail": "Invalid password"}, status=401)

        else:
            return Response({"detail": "Phone or Email required"}, status=400)

        # GENERATE TOKENS
        refresh = RefreshToken.for_user(user)

        # Fetch correct profile
        profile = None
        if user.account_type == "driver":
            profile = user.driver_profile
        elif user.account_type == "user":
            profile = user.rider_profile
        elif user.account_type == "restaurant":
            profile = user.restaurant_profile
        elif user.account_type == "repair":
            profile = user.repair_profile
        elif user.account_type == "pharmacy":
            profile = user.pharmacy_profile

        user_data = UserSerializer(user).data

        return Response({
            "detail": "Login successful",
            "user_id": user.id,
            "user": user_data,
            "account_type": user.account_type,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "profile_id": profile.id if profile else None,
            'verification_code': user.verification_code,
   
        }, status=200)

# class LoginView(APIView):
#     permission_classes = [AllowAny] 
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         print("LoginView request.data",request.data)
#         print("LoginView serializer.is_valid()", serializer.is_valid())
#         print("LoginView serializer.errors", serializer.errors)

        
#         if not serializer.is_valid():
#             print(serializer.errors,"serializer.errors")
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         phone = request.data.get('phone') 
#         email = request.data.get('email') 
#         verification_code = request.data.get('verification_code')
#         password = request.data.get('password')

#         # if email:
#         #     # Login with email and password
#         #     try:
#         #         user = CustomUser.objects.get(email=email)
#         #         # user = authenticate(request, email=email, password='22455')
#         #         print('user',user)
#         #         if user is not None:
#         #             # Generate access token
#         #             refresh = RefreshToken.for_user(user)
#         #             access_token = str(refresh.access_token)
#         #             return Response({
#         #                 'detail': 'Login successful',
#         #                 'access_token': access_token
#         #             }, status=status.HTTP_200_OK)
#         #         else:
#         #             return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
#         #     except ObjectDoesNotExist:

#         #         return Response({'detail': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
#         if email:
#             password = request.data.get("password")
#             print("Password received:", request.data.get("password"))
#             if not password:
#                 return Response({"detail": "Password required"}, status=status.HTTP_400_BAD_REQUEST)

#             # Authenticate using Django's built-in auth
#             user = authenticate(request, username=email, password=password)

#             if user is None:
#                 return Response({"detail": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

#             # Login successful → create tokens
#             refresh = RefreshToken.for_user(user)

#             return Response({
#                 "detail": "Login successful",
#                 "access_token": str(refresh.access_token),
#                 "refresh_token": str(refresh),
#                 "user": {
#                     "id": user.id,
#                     "email": user.email,
#                 }
#             }, status=status.HTTP_200_OK)
#         elif phone:
#             # Login with phone and verification code
            
#             try:
#                 user = CustomUser.objects.get(phone=phone)
    
#                 if verification_code:
#                     # Verify phone number using verification code
#                     if user.verification_code == verification_code:
#                         # Clear verification code after successful verification
#                         user.verification_code = user.generate_verification_code()
                        
#                         user.save()
#                         return Response({'detail': 'Verification successful','mes':'hi'}, status=status.HTTP_200_OK)
#                     else:
#                         return Response({'detail': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
#                 else:
#                     # Generate and send verification code
#                     user.generate_verification_code()
                   
#                     return Response({
#                         'detail': 'Verification code sent',
#                         'verification_code': user.verification_code,
#                         'account_type': user.account_type

#                     }, status=status.HTTP_200_OK)
#             except ObjectDoesNotExist:
            
#                 return Response({'detail': 'User with this phone number does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
#         else:
#             return Response({'detail': 'Please provide either email or phone'}, status=status.HTTP_400_BAD_REQUEST)

# class VerifyLoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = VerifyLoginSerializer(data=request.data)
#         if serializer.is_valid():
#             phone = serializer.validated_data['phone']
           
#             verification_code = serializer.validated_data['verification_code']
#             try:
#                 user = CustomUser.objects.get(phone=phone, verification_code=verification_code)
#                 user.verification_code = None  # Clear the verification code after successful login
#                 user.save()
                
#                 # Generate access token
#                 refresh = RefreshToken.for_user(user)
#                 access_token = str(refresh.access_token)
#                 refresh_token = str(refresh)

#                 user_data = UserSerializer(user).data  # Serialize the user data
#                 return Response({
#                     'detail': 'Login successful',
#                     'user': user_data,
#                     'access_token': access_token,
#                     'refresh_token': refresh_token
#                 }, status=status.HTTP_200_OK)
#             except CustomUser.DoesNotExist:
#                 return Response({'detail': 'Invalid verification code or phone number'}, status=status.HTTP_400_BAD_REQUEST)
#         print(serializer.errors)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyLoginSerializer(data=request.data)
        if serializer.is_valid():
            email_or_phone = serializer.validated_data.get('email_or_phone')
            verification_code = serializer.validated_data['verification_code']
            print("VerifyLoginView email_or_phone",email_or_phone)
            print("VerifyLoginView verification_code",verification_code)
            
            try:
                if '@' in email_or_phone:
                    # Assume email verification
                    user = CustomUser.objects.get(email=email_or_phone, verification_code=verification_code)
                else:
                    # Assume phone verification
                    user = CustomUser.objects.get(phone=email_or_phone, verification_code=verification_code)
                
                user.verification_code = None  # Clear the verification code after successful login
                user.save()
                
                # Generate access token
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                user_data = UserSerializer(user).data  # Serialize the user data
                return Response({
                    'detail': 'Login successful',
                    'user': user_data,
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({'detail': 'Invalid verification code or email/phone number'}, status=status.HTTP_400_BAD_REQUEST)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class VerifyLoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = VerifyLoginSerializer(data=request.data)
#         if serializer.is_valid():
#             print('Verifying login', serializer.validated_data)
#             email_or_phone = serializer.validated_data.get('email_or_phone')
#             print('email_or_phone',email_or_phone)
#             verification_code = serializer.validated_data['verification_code']
            
#             try:
#                 user = (CustomUser.objects.get(email=email_or_phone) if '@' in email_or_phone 
#                         else CustomUser.objects.get(phone=email_or_phone))
#                 print('user'  )
#                 if user.verification_code == verification_code:
#                     user.verification_code = verification_code  # Clear the code
#                     user.save()
                    
#                     refresh = RefreshToken.for_user(user)
#                     access_token = str(refresh.access_token)
#                     refresh_token = str(refresh)
                    
#                     user_data = UserSerializer(user).data  # Serialize user data
#                     return Response({
#                         'detail': 'Login successful',
#                         'user': user_data,
#                         'access_token': access_token,
#                         'refresh_token': refresh_token
#                     }, status=status.HTTP_200_OK)
#                 return Response({'detail': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
            
#             except CustomUser.DoesNotExist:
#                 return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
 
    permission_classes = [IsAuthenticated]
    serializer_class = EditProfileSerializer

    def get_object(self):
        """Ensure this returns a single user instance, not a queryset"""
        return self.request.user  # This returns the logged-in user instance

    def update(self, request, *args, **kwargs):
        """Handles profile updates"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()  # Ensure it's a single instance
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)  # Debugging step
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Requires authentication for all operations

class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

from rest_framework import viewsets
# from .models import Driver
class DriverViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(account_type="driver")
    serializer_class = DriverSerializer

class PersonalInfoViewSet(viewsets.ModelViewSet):
    queryset = PersonalInfo.objects.all()
    serializer_class = PersonalInfoSerializer

class VehicleInfoViewSet(viewsets.ModelViewSet):
    queryset = VehicleInfo.objects.all()
    serializer_class = VehicleInfoSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class UploadViewSet(viewsets.ModelViewSet):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = serializer.save()
        if user.user_type == 'driver':
            DriverProfile.objects.create(user=user)
        elif user.user_type == 'rider':
            RiderProfile.objects.create(user=user)

class DriverProfileViewSet(viewsets.ModelViewSet):
    queryset = DriverProfile.objects.all()
    serializer_class = DriverProfileSerializer
    # permission_classes = [IsAuthenticated]

from django.shortcuts import get_object_or_404
from rest_framework import views, status
from rest_framework.response import Response
from .models import DriverProfile, CustomUser
from .serializers import DriverProfileSerializer


class DriverProfileByIdView(views.APIView):
    def get(self, request, id, *args, **kwargs):
        user = get_object_or_404(CustomUser, id=id)
        driver_profile = get_object_or_404(DriverProfile, driver=user)
        serializer = DriverProfileSerializer(driver_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class RiderProfileByIdView(views.APIView):
    def get(self, request, id, *args, **kwargs):
        rider = get_object_or_404(CustomUser, id=id)
        rider_profile = get_object_or_404(RiderProfile, user=rider)
        serializer = RiderProfileSerializer(rider_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RiderProfileViewSet(viewsets.ModelViewSet):
    queryset = RiderProfile.objects.all()
    serializer_class = RiderProfileSerializer
    permission_classes = [IsAuthenticated]

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, format=None):
        user = request.user
        try:
            # Delete related data first (optional - Django will cascade delete)
            if hasattr(user, 'driverprofile'):
                user.driverprofile.delete()
            if hasattr(user, 'riderprofile'):
                user.riderprofile.delete()
            
            # Delete PersonalInfo, VehicleInfo, Documents if they exist
            PersonalInfo.objects.filter(driver=user).delete()
            VehicleInfo.objects.filter(driver=user).delete()
            Document.objects.filter(driver=user).delete()
            
            # Delete DriverOnline record if exists
            DriverOnline.objects.filter(driver=user).delete()
            
            # Delete the user account
            user.delete()
            
            return Response(
                {'detail': 'Account deleted successfully'}, 
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'detail': f'Error deleting account: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DeleteAccountByIdView(APIView):
    """Admin view to delete any user account by ID"""
    permission_classes = [IsAuthenticated]  # Add admin permission if needed

    def delete(self, request, user_id, format=None):
        user = get_object_or_404(CustomUser, id=user_id)
        try:
            # Delete related data
            if hasattr(user, 'driverprofile'):
                user.driverprofile.delete()
            if hasattr(user, 'riderprofile'):
                user.riderprofile.delete()
            
            PersonalInfo.objects.filter(driver=user).delete()
            VehicleInfo.objects.filter(driver=user).delete()
            Document.objects.filter(driver=user).delete()
            DriverOnline.objects.filter(driver=user).delete()
            
            user.delete()
            
            return Response(
                {'detail': 'User account deleted successfully'}, 
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'detail': f'Error deleting user account: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# class CreateAllDataView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = CreateAllDataSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         print(serializer.errors)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

 
import json
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class CreateAllDataView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs): 
        try:
            # Parse JSON data
            personal_info = json.loads(request.data.get('personal_info', '{}'))
            vehicle_info = json.loads(request.data.get('vehicle_info', '{}'))
            user_id = json.loads(request.data.get('user_id'))

            # Save PersonalInfo and VehicleInfo as before
            user = CustomUser.objects.get(id=user_id)
            personal_info_obj = PersonalInfo.objects.create(driver=user, **personal_info)
            vehicle_info_obj = VehicleInfo.objects.create(driver=user, **vehicle_info)

            # Save each document by its key as document_type
            created_documents = []
            for key in request.FILES:
                files = request.FILES.getlist(key)
                for file in files:
                    doc = Document.objects.create(
                        driver=user,
                        document_type=key,
                        document_file=file
                    )
                    created_documents.append(doc)

            return Response({
                'personal_info': PersonalInfoSerializer(personal_info_obj).data,
                'vehicle_info': VehicleInfoSerializer(vehicle_info_obj).data,
                'documents': DocumentSerializer(created_documents, many=True).data
            }, status=status.HTTP_201_CREATED)

        except json.JSONDecodeError as e:
            return Response(
                {'error': f'Invalid JSON format: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"Error processing request: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GetDriverVehicleInfoByIdViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        try:
            vehicle_info = VehicleInfo.objects.get(driver=pk)
            serializer = VehicleInfoSerializer(vehicle_info)
            return Response(serializer.data)
        except VehicleInfo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
# GetDriverInfoByIdViewSet 
class GetDriverInfoByIdViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        try:
            vehicle_info = PersonalInfo.objects.get(driver=pk)
            serializer = PersonalInfoSerializer(vehicle_info)
            return Response(serializer.data)
        except PersonalInfo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        

class UpdateUserProfileView(APIView):
    """API to update user profile (name, email, phone)"""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully", "user": serializer.data}, status=status.HTTP_200_OK)
        print('serializer.errors', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 

class DriverDocumentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        documents = Document.objects.filter(driver=user)
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class APKUploadView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
   
        apk = APKUpload.objects.all()
        serializer = APKUploadSerializer(apk, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password

 
from .serializers import ForgotPasswordSerializer
from .utils import send_temporary_password_email


class ForgotPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        print("ForgotPasswordView email",email)

        try:
            user = CustomUser.objects.get(email=email)

            # Generate temporary password
            temp_password = str(random.randint(100000, 999999))

            # Update user password
            user.password = make_password(temp_password)
            user.save()

            # Send email
            send_temporary_password_email(email, temp_password)
            print('Temporary password sent:', temp_password)
            return Response(

                {"detail": "Temporary password sent to your email"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print('e')
            return Response(
                {"detail": "Failed to process request", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
