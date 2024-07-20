 
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist

from accounts import send_verification_code
from chat.models import DriverOnline
from .models import CustomUser, DriverProfile, PersonalInfo, Profile, RiderProfile, Upload, VehicleInfo,Document
from .serializers import CreateAllDataSerializer, DocumentSerializer, DriverProfileSerializer, DriverSerializer, PersonalInfoSerializer, RegisterSerializer, RiderProfileSerializer, UploadSerializer, UserSerializer, VehicleInfoSerializer, VerifyLoginSerializer, ProfileSerializer

class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save() 
            # Generate and save verification code
            verification_code = user.generate_verification_code()

            # Send verification code via email
            send_mail(
                'Verification Code',
                f'Your verification code is {verification_code}',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )

            # Generate access token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # Create DriverOnline instance    
            DriverOnline.objects.create(
                driver=user,
                phone=request.data.get('phone'),  # Ensure phone number is part of registration data
                location=request.data.get('location'),  # Default location, adjust as needed
                latitude=request.data.get('latitude'),     # Default latitude, adjust as needed
                longitude=request.data.get('longitude'),   # Default longitude, adjust as needed
                rideType='Car'
            )

            return Response({
                'detail': 'User created successfully',
                'access_token': access_token,
                'verification_code': verification_code
            }, status=status.HTTP_201_CREATED)
        # print(serializer.errors)
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

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        email = request.data.get('email')
        verification_code = request.data.get('verification_code')
        password = request.data.get('password')

        if email:
            # Login with email and password
            try:
                user = CustomUser.objects.get(email=email)
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    # Generate access token
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    return Response({
                        'detail': 'Login successful',
                        'access_token': access_token
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            except ObjectDoesNotExist:
                return Response({'detail': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        elif phone:
            # Login with phone and verification code
            try:
                user = CustomUser.objects.get(phone=phone)
                if verification_code:
                    # Verify phone number using verification code
                    if user.verification_code == verification_code:
                        # Clear verification code after successful verification
                        user.verification_code = None
                        user.save()
                        return Response({'detail': 'Verification successful'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'detail': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Generate and send verification code
                    user.generate_verification_code()
                    print(user.verification_code)
                    return Response({
                        'detail': 'Verification code sent',
                        'verification_code': user.verification_code
                    }, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({'detail': 'User with this phone number does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return Response({'detail': 'Please provide either email or phone'}, status=status.HTTP_400_BAD_REQUEST)

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
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = RiderProfile.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        print('self',self.request.user.thumbnail)   
        lol =RiderProfile.objects.filter(user = self.request.user) 
        return RiderProfile.objects.filter(user = self.request.user)
        # return Response(self.request.user, status=status.HTTP_400_BAD_REQUEST)
    
    

    def update(self, request, *args, **kwargs):
         
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        # print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class RiderProfileViewSet(viewsets.ModelViewSet):
    queryset = RiderProfile.objects.all()
    serializer_class = RiderProfileSerializer
    permission_classes = [IsAuthenticated]



class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, format=None):
        user = get_object_or_404(CustomUser, id=request.user.id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class CreateAllDataView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CreateAllDataSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




    