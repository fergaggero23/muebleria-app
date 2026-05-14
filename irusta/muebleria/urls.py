from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from core import views

router = routers.DefaultRouter()
router.register(r'productos', views.ProductoViewSet)
router.register(r'clientes', views.ClienteViewSet)
router.register(r'ventas', views.VentaViewSet)
router.register(r'compras', views.CompraViewSet)
router.register(r'proveedores', views.ProveedorViewSet)
router.register(r'gastos', views.GastoViewSet)
router.register(r'detalleventa', views.DetalleVentaViewSet)
router.register(r'detallecompra', views.DetalleCompraViewSet)
router.register(r'notacredito', views.NotaCreditoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]