from django.urls import path,include
from .views import *
 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
) 
from rest_framework.routers import DefaultRouter
from .views import DriverViewSet

router = DefaultRouter()
router.register(r'drivers', DriverViewSet)
 
# router.register(r'userswe', UserViewSet)
router.register(r'driver-profiles', DriverProfileViewSet)
router.register(r'rider-profiles', RiderProfileViewSet)
 
 
router.register(r'personal-info', PersonalInfoViewSet)
router.register(r'vehicle-info', VehicleInfoViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'uploads', UploadViewSet)
router.register(r'driver-info-by-id', GetDriverInfoByIdViewSet, basename='driver-info-by-id')
router.register(r'vehicles-info-by-id', GetDriverVehicleInfoByIdViewSet, basename='vehicleinfo-by-id')


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-login/', VerifyLoginView.as_view(), name='verify-login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('delete-user/', DeleteUserView.as_view(), name='delete-user'),
    path('create-all/', CreateAllDataView.as_view(), name='create-all'),
    path('', include(router.urls)),
    path('driver-profile/<int:id>/', DriverProfileByIdView.as_view(), name='driver-profile-by-id'),
    path('rider-profile/<int:id>/', RiderProfileByIdView.as_view(), name='rider-profile-by-id'),
    path('update-profile/', UpdateUserProfileView.as_view(), name='update-profile'),

]