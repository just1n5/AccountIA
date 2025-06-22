"""
URLs para la aplicación de declaraciones.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeclarationViewSet, IncomeRecordViewSet

app_name = 'declarations'

router = DefaultRouter()
router.register(r'declarations', DeclarationViewSet, basename='declaration')

# URLs anidadas para income records
declaration_router = DefaultRouter()
declaration_router.register(
    r'income-records',
    IncomeRecordViewSet,
    basename='declaration-income-records'
)

urlpatterns = [
    path('', include(router.urls)),
    path('declarations/<str:declaration_pk>/', include(declaration_router.urls)),
]
