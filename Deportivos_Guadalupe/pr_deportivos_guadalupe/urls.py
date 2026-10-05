from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URLs a nivel de Proyecto
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    
    # URLs a nivel de App (Prefijo /guadalupe/)
    path('guadalupe/', include('app_deportivos_guadalupe.urls')),
    path('guadalupe/', include('app_transferencia.urls')),
    ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()