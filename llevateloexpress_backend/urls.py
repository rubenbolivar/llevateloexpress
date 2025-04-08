"""
URL configuration for llevateloexpress_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints
    path('api/products/', include('products.urls')),
    path('api/financing/', include('financing.urls')),
    path('api/users/', include('users.urls')),
    # Servir archivos HTML estáticos
    path('', TemplateView.as_view(template_name='index.html')),
    path('catalogo.html', TemplateView.as_view(template_name='catalogo.html')),
    path('detalle-producto.html', TemplateView.as_view(template_name='detalle-producto.html')),
    path('planes.html', TemplateView.as_view(template_name='planes.html')),
    path('calculadora.html', TemplateView.as_view(template_name='calculadora.html')),
    path('registro.html', TemplateView.as_view(template_name='registro.html')),
    path('nosotros.html', TemplateView.as_view(template_name='nosotros.html')),
    path('contacto.html', TemplateView.as_view(template_name='contacto.html')),
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
