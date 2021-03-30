from django.db.models import *
from django.contrib.auth.models import User
from django.urls import reverse


class Product(Model):
    name = CharField(max_length=80)
    price = DecimalField(max_digits=5, decimal_places=2)
    in_stock = PositiveIntegerField(default=0)
    image = ImageField(upload_to='user_media', default='default.jpg')

    def __str__(self):
        return '"%s", %s RUB' % (self.name, self.price)


class Order(Model):
    client = ForeignKey(User, on_delete=CASCADE, default=1)
    address = CharField(max_length=500)
    phone = CharField(max_length=13, default="Not provided")
    created = DateTimeField('creation timestamp', auto_now_add=True)

    def cost(self):
        return sum(item.cost() for item in self.items.all())


class OrderItem(Model):
    order = ForeignKey(Order, on_delete=CASCADE, related_name='items')
    product = ForeignKey(Product, on_delete=CASCADE, related_name='ordered')
    quantity = PositiveIntegerField(default=1)

    def cost(self):
        return self.product.price * self.quantity
