from django.db import models
from django.utils import timezone

from AuthUser.models import Client, SalesRep


# Create your models here.

class DailyIndicators(models.Model):
    date = models.DateField(unique=True)
    uf = models.DecimalField(max_digits=10, decimal_places=2)
    dolar = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.date} → UF: {self.uf}, USD: {self.dolar}"


class Product(models.Model):
    code = models.CharField("Codigo", max_length=255, unique=True)
    material_number = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField("Descripcion", max_length=255)
    price = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.code[:20]}: {self.description[:40]}..."


class Quote(models.Model):
    status_choices = [
        ("AP", "Aprobada"),
        ("RJ", "Rechazada"),
        ("WT", "En espera"),
        ("CL", "Cerrada"),
    ]
    currency_choices = [
        ("USD", "USD"),
        ("CLP", "CLP"),
        ("UF", "UF"),
    ]
    client = models.ForeignKey("AuthUser.Entity", verbose_name="Cliente", on_delete=models.CASCADE)
    salesRep = models.ForeignKey("AuthUser.SalesRep", verbose_name="Rep. Ventas", on_delete=models.CASCADE, related_name='sales_rep')
    status = models.CharField("Estado", max_length=50, choices=status_choices, default="WT")
    date = models.DateField("Fecha", auto_now=True)
    approved_by = models.ForeignKey("AuthUser.SalesRep", verbose_name="Aprobador", on_delete=models.CASCADE, default=1, related_name='manager')
    currency = models.CharField("Moneda", max_length=50, choices=currency_choices, default="USD")
    
    total_net = models.DecimalField("Subtotal", default=0, max_digits=20, decimal_places=2)
    iva = models.DecimalField("IVA", default=0, max_digits=20, decimal_places=2)
    final = models.DecimalField("Total", default=0, max_digits=20, decimal_places=2)
    

    @property
    def has_discounted_items(self):
        return any(pq.discount > 0 for pq in self.products.all())
    
    def is_editable(self):
        return (
            self.status == "WT"
            or (self.status == "AP" and self.approved_by == self.salesRep)
        )
    
    def approve_by_manager(self, manager):
        if self.status != "CL":
            self.status = "AP"
            self.approved_by = manager
            self.save()

    def reject(self, manager):
        if self.status != "CL":
            self.status = "RJ"
            self.approved_by = manager
            self.save()

    def close(self):
        if self.status != "CL":
            self.status = "CL"
            self.save()

    def __str__(self):
        return f"{timezone.now().year}-{self.pk:04d}"


class ProductQuote(models.Model):
    product = models.ForeignKey("Product", verbose_name="Producto", on_delete=models.CASCADE)
    quote = models.ForeignKey("Quote", verbose_name="Cotizacion", on_delete=models.CASCADE, related_name='products')
    discount = models.PositiveIntegerField("Descuento", default=0)
    profit_margin = models.PositiveIntegerField("GM%", default=35) # 35%
    unit_price = models.DecimalField("Precio unitario", max_digits=20, decimal_places=2)
    quantity = models.PositiveIntegerField("Cantidad", default=1)
    subtotal = models.DecimalField("Subtotal", max_digits=20, decimal_places=2)

    def __str__(self):
        return f"{self.product.code}: {self.product.description}"
    
    @property
    def computed_subtotal(self):
        return self.quantity * self.unit_price


class Template(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class TemplateProduct(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='template_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.code} x{self.quantity} in template {self.template.name}"
    