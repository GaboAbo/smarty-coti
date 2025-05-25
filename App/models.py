from django.db import models


regions = [
    ("I", "Region de Tarapaca"),
    ("II", "Region de Antofagasta"),
    ("III", "Region de Atacama"),
    ("IV", "Region de Coquimbo"),
    ("V", "Region de Valparaiso"),
    ("RM", "Region Metropolitana de Santiago"),
    ("VI", "Region del Libertador General Bernardo OHiggins"),
    ("VII", "Region del Maule"),
    ("VIII", "Region del Biobio"),
    ("IX", "Region de La Araucania"),
    ("X", "Region de Los Lagos"),
    ("XI", "Region de Aysen del General Carlos Ibanez del Campo"),
    ("XII", "Region de Magallanes y de la Antartica Chilena"),
    ("XIV", "Region de Los Rios"),
    ("XV", "Region de Arica y Parinacota"),
    ("XVI", "Region de Nuble")
]


class Entity(models.Model):
    """
    Hospital/Clinic/Institute, stores its information
    name: Entity's name
    address: Entity's address
    """
    name = models.CharField("Nombre", max_length=255)
    address = models.CharField("Direccion", max_length=255, choices=regions)

    class Meta:
        verbose_name = "Entidad"
        verbose_name_plural = "Entidades"

    def __str__(self):
        return self.name


class Client(models.Model):
    entity = models.ForeignKey("Entity", verbose_name="Entidad", on_delete=models.CASCADE)
    name = models.CharField("Nombre", max_length=255)
    email_address = models.CharField("Correo", max_length=255)

    def __str__(self):
        return f"{self.entity.name}"
    

class SalesRep(models.Model):
    name = models.CharField("Nombre", max_length=255)
    email_address = models.CharField("Correo", max_length=255)

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    code = models.CharField("Codigo", max_length=50, unique=True)
    material_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField("Descripcion", max_length=255)
    price = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.code[:20]}: {self.description[:40]}..."


class Quote(models.Model):
    public_id = models.PositiveIntegerField("Numero", unique=True)
    client = models.ForeignKey("Client", verbose_name="Cliente", on_delete=models.CASCADE)
    salesRep = models.ForeignKey("SalesRep", verbose_name="Rep. Ventas", on_delete=models.CASCADE)
    date = models.DateField("Fecha", auto_now=True)
    total = models.PositiveIntegerField("Total", default=0)

    def __str__(self):
        return f"Cotizacion #{self.pk}: {self.client.name} {self.total}"


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
    