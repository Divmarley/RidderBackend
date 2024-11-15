 
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
from food.models import Details, Image, Location, Rating, Restaurant
from .models import CustomUser, DriverProfile, PersonalInfo, Profile, RiderProfile, Upload, VehicleInfo,Document
from .serializers import CreateAllDataSerializer, DocumentSerializer, DriverProfileSerializer, DriverSerializer, LoginSerializer, PersonalInfoSerializer, RegisterSerializer, RiderProfileSerializer, UploadSerializer, UserSerializer, VehicleInfoSerializer, VerifyLoginSerializer, ProfileSerializer

class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            
            user = serializer.save() 
            # Generate and save verification code
            # verification_code = user.generate_verification_code()

            # Send verification code via email
            # send_mail(
            #     'Verification Code',
            #     f'Your verification code is {user.verification_code}',
            #     'from@example.com',
            #     [user.email],
            #     fail_silently=False,
            # )

            # Generate access token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # Create DriverOnline instance   

            print("user",user.account_type) 

            if user.account_type=='driver':

                DriverOnline.objects.create(
                    driver=user,
                    phone=request.data.get('phone'),  # Ensure phone number is part of registration data
                    location=request.data.get('location'),  # Default location, adjust as needed
                    latitude=request.data.get('latitude'),     # Default latitude, adjust as needed
                    longitude=request.data.get('longitude'),   # Default longitude, adjust as needed
                    push_token=request.data.get('push_token'),
                    # rideType='Car'
                )
                
            # Create Restaurant instance if the account type is 'restaurants'
            elif user.account_type == 'restaurants':
                # Create associated Image, Rating, Details, and Location instances
                image = Image.objects.create(
                    uri=request.data.get('image_uri'),
                    border_radius=request.data.get('border_radius', 10)
                )
                
                rating = Rating.objects.create(
                    value=request.data.get('rating_value', 0.0),
                    number_of_ratings=request.data.get('number_of_ratings', 0)
                )
                
                details = Details.objects.create(
                    name=request.data.get('restaurant_name'),
                    price_range=request.data.get('price_range', '$0 - $100'),
                    delivery_time=request.data.get('delivery_time', '20-30 mins')
                )
                
                location = Location.objects.create(
                    address=request.data.get('address'),
                    city=request.data.get('city'),
                    country=request.data.get('country'),
                    coordinates={
                        'latitude': request.data.get('latitude', '0.0'),
                        'longitude': request.data.get('longitude', '0.0')
                    }
                )

                # Create Restaurant with all related information
                Restaurant.objects.create(
                    user=user,
                    available=request.data.get('available', 'open'),
                    image=image,
                    rating=rating,
                    details=details,
                    location=location,
                    cuisine=request.data.get('cuisine', 'International'),
                    is_open=request.data.get('is_open', True),
                    about_us=request.data.get('about_us', 'About us text'),
                    delivery_fee=request.data.get('delivery_fee', '5.00'),
                )
                
            print('verification_code', user.verification_code)
            return Response({
                'detail': 'User created successfully',
                'access_token': access_token,
                'verification_code': user.verification_code,
                'id': user.id
            }, status=status.HTTP_201_CREATED) 
        print(serializer.errors)
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
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                print("User", user)
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
                    # user.generate_verification_code()
                    # print(user.verification_code)
                    return Response({
                        'detail': 'Verification code sent',
                        'verification_code': user.verification_code
                    }, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                print()
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



# class VerifyLoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = VerifyLoginSerializer(data=request.data)
#         if serializer.is_valid():
#             email_or_phone = serializer.validated_data.get('email_or_phone')
#             verification_code = serializer.validated_data['verification_code']
            
#             try:
#                 if '@' in email_or_phone:
#                     # Assume email verification
#                     user = CustomUser.objects.get(email=email_or_phone, verification_code=verification_code)
#                 else:
#                     # Assume phone verification
#                     user = CustomUser.objects.get(phone=email_or_phone, verification_code=verification_code)
                
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
#                 return Response({'detail': 'Invalid verification code or email/phone number'}, status=status.HTTP_400_BAD_REQUEST)
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
                user = (CustomUser.objects.get(email=email_or_phone) if '@' in email_or_phone 
                        else CustomUser.objects.get(phone=email_or_phone))
                
                if user.verification_code == verification_code:
                    user.verification_code = None  # Clear the code
                    user.save()
                    
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    refresh_token = str(refresh)
                    
                    user_data = UserSerializer(user).data  # Serialize user data
                    return Response({
                        'detail': 'Login successful',
                        'user': user_data,
                        'access_token': access_token,
                        'refresh_token': refresh_token
                    }, status=status.HTTP_200_OK)
                return Response({'detail': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
            
            except CustomUser.DoesNotExist:
                return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = RiderProfile.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        print('self',self.request.user.thumbnail)    
        return RiderProfile.objects.filter(user = self.request.user)
        # return Response(self.request.user, status=status.HTTP_400_BAD_REQUEST) 

    def update(self, request, *args, **kwargs):
         
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        print(serializer)
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
        user = get_object_or_404(CustomUser, id=request.user.id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# class CreateAllDataView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = CreateAllDataSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         print(serializer.errors)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

 
from rest_framework.response import Response
from rest_framework import status

class CreateAllDataView(APIView):
    def post(self, request, *args, **kwargs):
        print("request", request.user.id)
        serializer = CreateAllDataSerializer(data=request.data, context={'user_id': request.user.id})
        if serializer.is_valid():
            data = serializer.save()
            return Response(data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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