from django.db import models
from django_extras.contrib.auth.models import SingleOwnerMixin

class A(SingleOwnerMixin, models.Model):
    name = models.CharField("name", max_length=255)

    def __unicode__(self):
        return self.name

class B(SingleOwnerMixin, models.Model):
    a = models.ForeignKey(A)
    name = models.CharField("name", max_length=255)

    def __unicode__(self):
        return self.name
    
class C(SingleOwnerMixin, models.Model):
    b = models.ForeignKey(B)
    name = models.CharField("name", max_length=255)

    def __unicode__(self):
        return self.name

