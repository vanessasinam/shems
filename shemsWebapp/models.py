from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cid = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    billing_address = models.CharField(max_length=100)

    class Meta:
        # Set the table name to the existing table name in PostgreSQL
        # managed = False
        db_table = 'customer'
    def _str_(self):
        return f"{self.first_name} {self.last_name}"

class Location(models.Model):
    # Define fields that match the columns in your existing table
    lid = models.AutoField(primary_key=True)
    num_bedrooms = models.IntegerField()
    num_occupants = models.IntegerField()
    area = models.IntegerField()
    unit = models.CharField(max_length=20)
    street = models.CharField(max_length=30)
    building = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    zipcode = models.CharField(max_length=5)

    class Meta:
        # Set the table name to the existing table name in PostgreSQL
        # managed = False
        db_table = 'location'
    def _str_(self):
        return f"{self.lid} {self.building} {self.street} {self.city}"
    

class CustomerLocation(models.Model):
    cid = models.ForeignKey(
        Customer, on_delete=models.CASCADE
    )
    lid = models.ForeignKey(
        Location, on_delete=models.CASCADE
    )
    class Meta:
        # Set the table name to the existing table name in PostgreSQL
        # managed = False
        db_table = 'customerlocation'

class DeviceModel(models.Model):
    # Define fields that match the columns in your existing table
    model_num = models.CharField(max_length=50, primary_key=True)
    model_type = models.CharField(max_length=50)
    properties = models.CharField(max_length=100)

    class Meta:
        # Set the table name to the existing table name in PostgreSQL
        managed = False
        db_table = 'devicemodel'

class Device(models.Model):
    # Define fields that match the columns in your existing table
    did = models.AutoField(primary_key=True)
    lid = models.ForeignKey(
        Location, on_delete=models.CASCADE
    )
    model_num = models.ForeignKey(
        DeviceModel, on_delete=models.CASCADE, related_name="number"
    )

    class Meta:
        # Set the table name to the existing table name in PostgreSQL
        # managed = False
        db_table = 'device'

