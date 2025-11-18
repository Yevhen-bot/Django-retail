# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.CharField(unique=True, max_length=30)
    birth_date = models.DateField()
    phone_number = models.CharField(unique=True, max_length=13)

    class Meta:
        abstract = True

class Client(Person):
    email = models.CharField(unique=True, max_length=30, blank=True, null=True)

    class Meta:
        db_table = 'client'

class Estimate(models.Model):
    pk = models.CompositePrimaryKey('item_id', 'worker_id')
    item = models.ForeignKey('Item', models.DO_NOTHING)
    worker = models.ForeignKey('Worker', models.DO_NOTHING)
    reasoning = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField()
    cost = models.DecimalField(max_digits=10, decimal_places=0)

    class Meta:
        db_table = 'estimate'

class Item(models.Model):
    description = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=25)

    class Meta:
        db_table = 'item'

class Operation(models.Model):
    operation = models.CharField(max_length=15)

    class Meta:
        db_table = 'operation'

class OperationHistory(models.Model):
    client = models.ForeignKey(Client, on_delete=models.RESTRICT)
    item = models.ForeignKey(Item, on_delete=models.RESTRICT)
    date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=0)
    operation = models.ForeignKey(Operation, on_delete=models.RESTRICT)
    info = models.CharField(max_length=255, blank=True, null=True)
    store = models.ForeignKey('Store', on_delete=models.RESTRICT)

    class Meta:
        db_table = 'operation_history'

class Role(models.Model):
    role = models.CharField(max_length=22)

    class Meta:
        db_table = 'role'

    def __str__(self):
        return self.role

class Store(models.Model):
    name = models.CharField(max_length=22)
    country = models.CharField(max_length=5)
    city = models.CharField(max_length=20)
    street = models.CharField(max_length=40)
    house_number = models.CharField(max_length=5)

    class Meta:
        db_table = 'store'

class Worker(Person):
    store = models.ForeignKey(Store, on_delete=models.RESTRICT)
    role = models.ForeignKey(Role, on_delete=models.RESTRICT)

    class Meta:
        db_table = 'worker'