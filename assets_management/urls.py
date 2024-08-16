from django.urls import path
from .views import AssetListCreateView, AssetDetailView, AssetImportView, AssetExportView

urlpatterns = [
    path('assets/', AssetListCreateView.as_view(), name='asset_list_create'),
    path('assets/<int:pk>/', AssetDetailView.as_view(), name='asset_detail'),
    path('assets/import/', AssetImportView.as_view(), name='asset-import'),
    path('assets/export/', AssetExportView.as_view(), name='asset-export'),
]
