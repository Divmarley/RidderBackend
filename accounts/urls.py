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


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-login/', VerifyLoginView.as_view(), name='verify-login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('delete-user/<int:user_id>/', DeleteUserView.as_view(), name='delete-user'),
    path('', include(router.urls)),
]