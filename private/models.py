from django.db import models
from public.models import MainTenant, SubTenant


class Contract(models.Model):
    dummy = models.CharField(max_length=19),
    test = models.CharField(max_length=2)
    # main_tenant = models.ForeignKey(MainTenant, on_delete=models.CASCADE)  # TODO: on_delete!?
    # sub_tenant = models.ForeignKey(SubTenant, on_delete=models.CASCADE)  # TODO: on_delete!?
