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
        return f"{self.name}"
    

class SalesRep(models.Model):
    name = models.CharField("Nombre", max_length=255)
    email_address = models.CharField("Correo", max_length=255)

    def __str__(self):
        return f"{self.name}"
    

class Group(models.Model):
    GENERATION_CHOICES = [
        ("OPT", "Optera (170)"),
        ("EX3", "Exera III (190)"),
        ("EX2", "Exera II (180)"),
        ("EX1", "Exera I (160)"),
        ("LUC", "Evis Lucera (270)"),
        ("LUE", "Evis Lucera Elite (290)"),
        ("EV3", "Evis Exera III (190)"),
        ("EV2", "Evis Exera II (180)"),
        ("VSR", "Visera (150/160)"),
        ("VSP", "Visera Pro"),
        ("VSE", "Visera Elite"),
        ("VS2", "Visera Elite II"),
        ("CV1", "Serie CV-100"),
        ("CV2", "Serie CV-200"),
        ("CV3", "Serie CV-300"),
        ("CV4", "Serie CV-400"),
    ]
    group_gen = models.CharField("Generacion", max_length=100, choices=GENERATION_CHOICES)

    def __str__(self):
        return f"{self.group_gen}"


class Product(models.Model):
    group = models.ForeignKey(
        Group,
        verbose_name="Grupo",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    code = models.CharField("Codigo", max_length=50, unique=True)
    description = models.CharField("Descripcion", max_length=255)
    price = models.PositiveIntegerField("Precio unitario dealer")

    def __str__(self):
        return f"{self.code}"


class Quote(models.Model):
    public_id = models.PositiveIntegerField("Numero", unique=True)
    client = models.ForeignKey("Client", verbose_name="Cliente", on_delete=models.CASCADE)
    salesRep = models.ForeignKey("SalesRep", verbose_name="Rep. Ventas", on_delete=models.CASCADE)
    date = models.DateField("Fecha", auto_now=True)
    total = models.PositiveIntegerField("Total", default=0)

    def __str__(self):
        return f"Cotizacion #{self.pk}: {self.client.name} {self.total}"


class ProductQuote(models.Model):
    group = models.ForeignKey("Group", verbose_name="Grupo", on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey("Product", verbose_name="Producto", on_delete=models.CASCADE)
    quote = models.ForeignKey("Quote", verbose_name="Cotizacion", on_delete=models.CASCADE, related_name='products')
    discount = models.PositiveIntegerField("Descuento", default=0)
    profit_margin = models.PositiveIntegerField("GM%", default=35) # 35%
    unit_price = models.PositiveIntegerField("Precio unitario")
    quantity = models.PositiveIntegerField("Cantidad", default=1)
    subtotal = models.PositiveIntegerField("Subtotal")

    def __str__(self):
        return f"{self.product.code}: {self.subtotal}"
    
    @property
    def computed_subtotal(self):
        return self.quantity * self.unit_price
