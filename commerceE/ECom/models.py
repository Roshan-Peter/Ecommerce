from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.


class Users(models.Model):
    name = models.CharField(max_length=250, unique=True, null=False)
    username = models.CharField(max_length=250, unique=True, null=False)
    email = models.CharField(max_length=250, unique=True, null=False)
    password = models.TextField(null=False)
    phone = models.IntegerField(null=True)
    class Meta:
        db_table = 'ecom_users'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class AdminUsers(models.Model):
    name = models.CharField(max_length=250, null=False)
    username = models.CharField(max_length=250, unique=True, null=False)
    password = models.TextField(null=False)
    email = models.TextField(null=False)
    class Meta:
        db_table = 'ecom_admin'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    

class Category(models.Model):
    name = models.CharField(null=False, unique=True, max_length=250)
    class Meta:
        db_table = 'ecom_category'


class Product(models.Model):
    name = models.CharField(null=False, max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(null= False)
    longDescription = models.TextField(null= True)
    image = models.TextField(null=True)
    price = models.BigIntegerField(null=False)
    class Meta:
        db_table = 'ecom_products'



class Country(models.Model):
    name = models.CharField(null=False, max_length=250)
    class Meta:
        db_table = 'ecom_country'



class Address(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    city = models.CharField(null=False)
    state = models.CharField(null=False)
    address = models.CharField(null=False)
    postal = models.CharField(null=False, unique=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    class Meta:
        db_table = 'ecom_address'



class Cart(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE,null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=False)
    count = models.IntegerField(null=True)
    class Meta:
        db_table = 'ecom_cart'


class Checkout(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE,null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    count = models.IntegerField(null=True)
    class Meta:
        db_table = 'ecom_checkout'
    