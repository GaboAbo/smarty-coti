from django.db import models
from django.utils import timezone

from AuthUser.models import Client, SalesRep


# Create your models here.
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
    client = models.ForeignKey("AuthUser.Entity", verbose_name="Cliente", on_delete=models.CASCADE)
    salesRep = models.ForeignKey("AuthUser.SalesRep", verbose_name="Rep. Ventas", on_delete=models.CASCADE, related_name='sales_rep')
    status = models.CharField("Estado", max_length=50, choices=status_choices, default="WT")
    date = models.DateField("Fecha", auto_now=True)
    approved_by = models.ForeignKey("AuthUser.SalesRep", verbose_name="Aprobador", on_delete=models.CASCADE, default=1, related_name='manager')
    total = models.PositiveIntegerField("Total", default=0)

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
    unit_price = models.PositiveIntegerField("Precio unitario")
    quantity = models.PositiveIntegerField("Cantidad", default=1)
    subtotal = models.PositiveIntegerField("Subtotal")

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
    