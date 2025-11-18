"""
URL configuration for lab3 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from main import views
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView

# router = DefaultRouter()
# router.register('stores', views.StoreViewSet, basename='store')
# urlpatterns = router.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/auth/', include('authentication.urls')),
    path('stores/<int:id>/', views.StoreDetailAPIView.as_view(), name='store-detail'),
    path('stores/', views.StoreListCreateUpdateAPIView.as_view(), name='store-list-create-update'),
    path('workers/<int:id>/', views.WorkerDetailAPIView.as_view(), name='worker-detail'),
    path('workers/', views.WorkerListCreateUpdateAPIView.as_view(), name='worker-list-create-update'),
    path('roles/<int:id>/', views.RoleDetailAPIView.as_view(), name='role-detail'),
    path('roles/', views.RoleListCreateUpdateAPIView.as_view(), name='role-list-create-update'),
    path('operations/<int:id>/', views.OperationDetailAPIView.as_view(), name='operation-detail'),
    path('operations/', views.OperationListCreateUpdateAPIView.as_view(), name='operation-list-create-update'),
    path('clients/<int:id>/', views.ClientDetailAPIView.as_view(), name='client-detail'),
    path('clients/', views.ClientListCreateUpdateAPIView.as_view(), name='client-list-create-update'),
    path('items/<int:id>/', views.ItemDetailAPIView.as_view(), name='item-detail'),
    path('items/', views.ItemListCreateUpdateAPIView.as_view(), name='item-list-create-update'),
    path('estimates/<int:id>/', views.EstimateDetailAPIView.as_view(), name='estimate-detail'),
    path('estimates/', views.EstimateListCreateUpdateAPIView.as_view(), name='estimate-list-create-update'),
    path('op-his/<int:id>/', views.OperationHistoryDetailAPIView.as_view(), name='operationhistory-detail'),
    path('op-his/', views.OperationHistoryListCreateUpdateAPIView.as_view(), name='operationhistory-list-create-update'),
    path('custom/<str:name>/', views.getList, name='custom-list'),
    path('custom/<str:name>/<int:id>/', views.deleteElement, name='custom-delete')
]
