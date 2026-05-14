from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from decimal import Decimal

# ======================
# CLIENTES
# ======================
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    dni_cuit = models.CharField(max_length=20, verbose_name="DNI/CUIT")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción opcional")

    def __str__(self):
        return self.nombre

    @property
    def historial_ventas(self):
        return self.ventas.all().order_by('-fecha')


# ======================
# PROVEEDORES
# ======================
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    dni_cuit = models.CharField(max_length=20, verbose_name="DNI/CUIT")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción opcional")

    def __str__(self):
        return self.nombre

    @property
    def historial_compras(self):
        return self.compras.all().order_by('-fecha')


# ======================
# PRODUCTOS
# ======================
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio de venta
    costo_promedio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField(default=0)
    codigo = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


# ======================
# VENTAS
# ======================
class Venta(models.Model):
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
        ('criptomonedas', 'Criptomonedas'),
    ]

    codigo = models.CharField(max_length=20, unique=True, editable=False)
    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)

    def save(self, *args, **kwargs):
        if not self.codigo:
            last = Venta.objects.order_by('-id').first()
            next_id = 1 if not last else last.id + 1
            self.codigo = f"V-{next_id:08d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.cliente.nombre}"


# ======================
# DETALLE VENTA
# ======================
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en {self.venta.codigo}"


# ======================
# COMPRAS
# ======================
class Compra(models.Model):
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
        ('criptomonedas', 'Criptomonedas'),
    ]

    codigo = models.CharField(max_length=20, unique=True, editable=False)
    fecha = models.DateTimeField(auto_now_add=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='compras')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)

    def save(self, *args, **kwargs):
        if not self.codigo:
            last = Compra.objects.order_by('-id').first()
            next_id = 1 if not last else last.id + 1
            self.codigo = f"C-{next_id:08d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.proveedor.nombre}"


# ======================
# DETALLE COMPRA
# ======================
class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.costo_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en {self.compra.codigo}"


# ======================
# GASTOS
# ======================
class Gasto(models.Model):
    fecha = models.DateField(auto_now_add=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return f"Gasto: {self.descripcion} - ${self.monto:.2f}"


# ======================
# NOTA DE CRÉDITO
# ======================
class NotaCredito(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aplicada', 'Aplicada'),
    ]

    codigo = models.CharField(max_length=20, unique=True, editable=False)
    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='notas_credito')
    venta = models.ForeignKey(Venta, on_delete=models.SET_NULL, null=True, blank=True, related_name='notas_credito')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    motivo = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    def save(self, *args, **kwargs):
        if not self.codigo:
            last = NotaCredito.objects.order_by('-id').first()
            next_id = 1 if not last else last.id + 1
            self.codigo = f"NC-{next_id:08d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.cliente.nombre}"


# ======================
# SEÑALES MEJORADAS
# ======================

# --- FUNCIONES AUXILIARES ---
def actualizar_total_venta(venta):
    with transaction.atomic():
        nuevo_total = sum(detalle.subtotal for detalle in venta.detalles.all())
        venta.total = nuevo_total
        venta.save(update_fields=['total'])


def actualizar_total_compra(compra):
    with transaction.atomic():
        nuevo_total = sum(detalle.subtotal for detalle in compra.detalles.all())
        compra.total = nuevo_total
        compra.save(update_fields=['total'])


# --- DETALLES DE VENTA ---
@receiver(post_save, sender=DetalleVenta)
def actualizar_stock_y_total_venta_on_save(sender, instance, created, **kwargs):
    with transaction.atomic():
        producto = instance.producto
        venta = instance.venta

        if created:
            # Verificar stock antes de vender
            if producto.stock < instance.cantidad:
                raise ValueError(f"No hay suficiente stock para {producto.nombre}. Disponible: {producto.stock}")
            producto.stock -= instance.cantidad
        else:
            # Si ya existía (edición), ajustar diferencia
            old_instance = DetalleVenta.objects.filter(id=instance.id).first()
            if old_instance:
                diff_cant = old_instance.cantidad - instance.cantidad
                producto.stock += diff_cant  # Ajustar: si bajó cantidad, devuelve stock; si subió, resta más
                if producto.stock < 0:
                    producto.stock = 0
                    raise ValueError("No se puede tener stock negativo tras edición.")

        producto.save()
        actualizar_total_venta(venta)


@receiver(post_delete, sender=DetalleVenta)
def actualizar_stock_y_total_venta_on_delete(sender, instance, **kwargs):
    with transaction.atomic():
        producto = instance.producto
        producto.stock += instance.cantidad
        producto.save()
        actualizar_total_venta(instance.venta)


# --- DETALLES DE COMPRA ---
@receiver(post_save, sender=DetalleCompra)
def actualizar_stock_y_costo_compra_on_save(sender, instance, created, **kwargs):
    with transaction.atomic():
        producto = instance.producto
        compra = instance.compra

        # Manejar cambios en cantidad
        old_instance = None
        if not created:
            try:
                old_instance = DetalleCompra.objects.get(id=instance.id)
            except DetalleCompra.DoesNotExist:
                pass

        if created:
            # Nueva entrada
            producto.stock += instance.cantidad
        else:
            # Edición: ajustar stock
            if old_instance:
                diff_cant = instance.cantidad - old_instance.cantidad
                producto.stock += diff_cant

        # Recalcular costo promedio solo si hay stock
        if producto.stock > 0:
            # Calcular costo total ponderado
            valor_actual = producto.stock * producto.costo_promedio
            # Restar el costo anterior de este detalle si ya existía
            if old_instance:
                valor_actual += old_instance.cantidad * old_instance.costo_unitario
            # Sumar nuevo costo
            valor_actual += instance.cantidad * instance.costo_unitario
            # Nuevo costo promedio
            producto.costo_promedio = valor_actual / producto.stock
        elif producto.stock == 0:
            producto.costo_promedio = 0

        producto.save()
        actualizar_total_compra(compra)


@receiver(post_delete, sender=DetalleCompra)
def actualizar_stock_y_costo_compra_on_delete(sender, instance, **kwargs):
    with transaction.atomic():
        producto = instance.producto
        producto.stock -= instance.cantidad

        if producto.stock <= 0:
            producto.costo_promedio = 0
            producto.stock = 0
        else:
            # Re-calcular costo promedio sin este detalle
            detalles_restantes = DetalleCompra.objects.filter(
                producto=producto,
                compra__in=Compra.objects.exclude(id=instance.compra.id)
            ) | DetalleCompra.objects.filter(compra=instance.compra).exclude(id=instance.id)

            if detalles_restantes.exists():
                total_valor = sum(d.cantidad * d.costo_unitario for d in detalles_restantes)
                producto.costo_promedio = total_valor / producto.stock
            else:
                producto.costo_promedio = 0

        producto.save()
        actualizar_total_compra(instance.compra)