"""
URL configuration for driverapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
 
def health_check(request):
    return JsonResponse({'status': 'ok'}, status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
 
     path('health/', health_check, name='health-check'),
    # path('api/', include('drivers.urls')),
    # path('api/', include('client.urls')),
    # path('api/', include('ride.urls')),

    
    path('api/', include('chat.urls')),
    path('api/', include('food.urls')),
    path('api/', include('ride.urls')),
    path('api/', include('pharmacy.urls')),
    path('', include('accounts.urls')), 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

 