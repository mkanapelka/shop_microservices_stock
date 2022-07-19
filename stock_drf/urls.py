"""stock_drf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from rest_framework import routers

from stock.views.category import CategoryApiView
from stock.views.characteristic import CharacteristicApiView
from stock.views.product import ProductAdminApiViewSet, ProductApiViewSet

product_router = routers.SimpleRouter()
product_admin_router = routers.SimpleRouter()

product_router.register(r'products', ProductApiViewSet)
product_admin_router.register(r'products_admin', ProductAdminApiViewSet)

print(product_router.urls)
print(product_admin_router.urls)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/', include(product_router.urls)),
    path('api/v1/', include(product_admin_router.urls)),

    path('api/v1/categories/', CategoryApiView.as_view()),
    path('api/v1/characteristics/', CharacteristicApiView.as_view()),
]
