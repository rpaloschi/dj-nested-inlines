from django.db import models
from django_extras.contrib.auth.models import SingleOwnerMixin

class FuncDistrShape(SingleOwnerMixin, models.Model):
    class Meta:
        verbose_name = "function distribution shape"
    # Initial values: Lognormal, Beta, Gamma
    name_fds = models.CharField(max_length=255)
    user_def = models.BooleanField(default=True, editable=False)

    def __unicode__(self):
        return self.name_fds


class A(SingleOwnerMixin, models.Model):
    name_a = models.CharField("name", max_length=255)

    def __unicode__(self):
        return '%s (by "%s")' % (self.name_a, self.owner.username)

class B(SingleOwnerMixin, models.Model):
    a = models.ForeignKey(A)
    name_b = models.CharField("name", max_length=255)

    def __unicode__(self):
        return self.name_b
    
class C(SingleOwnerMixin, models.Model):
    b = models.ForeignKey(B)
    name_c = models.CharField("name", max_length=255)
    func_distr_shape = models.ForeignKey(
       'FuncDistrShape',
       verbose_name='function distribution shape')

    def __unicode__(self):
        return self.name_c

