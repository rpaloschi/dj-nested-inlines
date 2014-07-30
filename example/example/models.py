from django.db import models
from django_extras.contrib.auth.models import SingleOwnerMixin

class A(SingleOwnerMixin, models.Model):
    name_a = models.CharField("name", max_length=255)

    def __unicode__(self):
        return self.name_a

class B(SingleOwnerMixin, models.Model):
    a = models.ForeignKey(A)
    name_b = models.CharField("name", max_length=255)

    def __unicode__(self):
        return self.name_b
    
class C(SingleOwnerMixin, models.Model):
    b = models.ForeignKey(B)
    name_c = models.CharField("name", max_length=255)

    def __unicode__(self):
        return self.name_c

