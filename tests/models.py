from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class RESTFrameworkModel(models.Model):
    """
    Base for test models that sets app_label, so they play nicely.
    """

    class Meta:
        app_label = 'tests'
        abstract = True


class BasicModel(RESTFrameworkModel):
    text = models.CharField(max_length=100, verbose_name=_("Text comes here"), help_text=_("Text description."))


class BaseFilterableItem(RESTFrameworkModel):
    text = models.CharField(max_length=100)

    class Meta:
        abstract = True


class FilterableItem(BaseFilterableItem):
    decimal = models.DecimalField(max_digits=4, decimal_places=2)
    date = models.DateField()


# Models for relations tests
# ManyToMany
class ManyToManyTarget(RESTFrameworkModel):
    name = models.CharField(max_length=100)


class ManyToManySource(RESTFrameworkModel):
    name = models.CharField(max_length=100)
    targets = models.ManyToManyField(ManyToManyTarget, related_name='sources')


# ManyToMany with inheritance and a through model
class ManyToManyThroughTarget(RESTFrameworkModel):
    name = models.CharField(max_length=100)


class ManyToManyThroughSource(ManyToManyThroughTarget):
    name2 = models.CharField(max_length=100)
    targets = models.ManyToManyField(ManyToManyThroughTarget,
                                     through='ManyToManyThrough',
                                     related_name='sources')


class ManyToManyThrough(RESTFrameworkModel):
    name = models.CharField(max_length=100)
    source = models.ForeignKey(ManyToManyThroughSource, related_name='through')
    target = models.ForeignKey(ManyToManyThroughTarget, related_name='through')


# ForeignKey
class ForeignKeyTarget(RESTFrameworkModel):
    name = models.CharField(max_length=100)


class ForeignKeySource(RESTFrameworkModel):
    name = models.CharField(max_length=100)
    target = models.ForeignKey(ForeignKeyTarget, related_name='sources',
                               help_text='Target', verbose_name='Target',
                               on_delete=models.CASCADE)


# Nullable ForeignKey
class NullableForeignKeySource(RESTFrameworkModel):
    name = models.CharField(max_length=100)
    target = models.ForeignKey(ForeignKeyTarget, null=True, blank=True,
                               related_name='nullable_sources',
                               verbose_name='Optional target object',
                               on_delete=models.CASCADE)


# OneToOne
class OneToOneTarget(RESTFrameworkModel):
    name = models.CharField(max_length=100)


class NullableOneToOneSource(RESTFrameworkModel):
    name = models.CharField(max_length=100)
    target = models.OneToOneField(OneToOneTarget, null=True, blank=True,
                                  related_name='nullable_source', on_delete=models.CASCADE)
