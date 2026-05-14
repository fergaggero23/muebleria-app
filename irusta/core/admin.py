from django.contrib import admin
from .models import (
    Producto,
    Cliente,
    Proveedor,
    Venta,
    DetalleVenta,
    Compra,
    DetalleCompra,
    NotaCredito,
    Gasto
)

admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Proveedor)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(Compra)
admin.site.register(DetalleCompra)
admin.site.register(NotaCredito)
admin.site.register(Gasto)