"""
Models for the AuthUser app.

Includes custom user models for Engineers and Clients who are associated with entities.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


# Create your models here.
class Entity(models.Model):
    """
    Hospital/Clinic/Institute, stores its information
    name: Entity's name
    address: Entity's address
    """
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
    
    name = models.CharField("Nombre", max_length=255)
    address = models.CharField("Direccion", max_length=255)
    region = models.CharField("Region", max_length=255, choices=regions, default="RM")

    class Meta:
        verbose_name = "Entidad"
        verbose_name_plural = "Entidades"

    def __str__(self):
        return self.name
    

class EnterpriseUser(models.Model):
    """
    Abstract base model for users belonging to an entity (company or institution).

    Attributes:
        entity (Entity): The entity (organization) the user is associated with.
        role (str): The user's role within the entity, chosen from predefined choices.
    """

    ROLE_CHOICES = [
        ("MAN", "Gerente"),
        ("ENG", "Ingeniero/a"),
        ("REP", "Rep. Ventas"),
        ("ADM", "Administrativo"),
        ("BOS", "Jefe/a de unidad"),
        ("SUP", "Supervisor/a"),
        ("DOC", "Doctor/a"),
        ("NUR", "Enfermero/a"),
        ("TEN", "Tens"),
    ]

    entity = models.ForeignKey(
        Entity,
        verbose_name="Entidad",
        on_delete=models.CASCADE
    )
    role = models.CharField(
        "Cargo",
        max_length=50,
        choices=ROLE_CHOICES
    )

    class Meta:
        abstract = True


class SalesRep(EnterpriseUser, AbstractUser):
    """
    Model representing an Sales representative, extending the base Django user and EnterpriseUser.

    Attributes:
        groups (ManyToMany): Groups the engineer belongs to.
        user_permissions (ManyToMany): Permissions specific to the engineer.
    """

    groups = models.ManyToManyField(
        Group,
        related_name='salesrep_set',
        blank=True,
        help_text='The groups this engineer belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='salesrep_set',
        blank=True,
        help_text='Specific permissions for this representative.',
        verbose_name='user permissions',
    )

    class Meta:
        verbose_name = "Ingeniero"
        verbose_name_plural = "Ingenieros"

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Client(EnterpriseUser):
    """
    Model representing a client user.

    Attributes:
        name (str): Client’s name.
    """

    name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"{self.name}"
