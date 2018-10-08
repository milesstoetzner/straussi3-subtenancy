from django.db import models, migrations


class MainTenant(models.Model):
    # Information about main tenant
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    tenant_id = models.PositiveIntegerField()
    RESIDENTIAL_HOME_TYPE_CHOICES = (('str3', 'Straußäcker 3'),)
    residential_home = models.CharField(max_length=10, choices=RESIDENTIAL_HOME_TYPE_CHOICES)
    begin_rent_agreement = models.DateField()
    end_rent_agreement = models.DateField()
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)

    # Information about subtenancy
    house_number = models.CharField(max_length=2)
    room_number = models.CharField(max_length=3)
    begin_subtenancy = models.DateField()
    end_subtenancy = models.DateField()
    comeback = models.BooleanField()
    rent = models.PositiveIntegerField()
    room_condition = models.BooleanField()

    # TODO: Main Tenant Validation
    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' (' + str(self.tenant_id) + ')'


class SubTenant(models.Model):
    # Information about sub tenant
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    birthday = models.DateField()
    nationality = models.CharField(max_length=100)
    eu = models.BooleanField()
    student_id = models.PositiveIntegerField()
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)

    # Information about subtenancy
    begin_subtenancy = models.DateField()
    end_subtenancy = models.DateField()

    # Correspondence address
    name = models.CharField(max_length=250)
    street = models.CharField(max_length=250)
    house_number = models.CharField(max_length=10)
    postcode = models.PositiveIntegerField()
    city = models.CharField(max_length=250)
    country = models.CharField(max_length=250)

    # TODO: Sub Tenant Validation

    def __str__(self):
        return self.first_name + ' ' + self.last_name + '(' + str(self.birthday) + ')'