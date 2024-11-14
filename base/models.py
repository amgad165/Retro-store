from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    display_order = models.PositiveIntegerField(default=999)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['display_order', 'name']


class Section(models.Model):
    name = models.CharField(max_length=255, unique=True)
    data_filter = models.CharField(max_length=255,unique=True, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=999)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['display_order', 'name']


class Color(models.Model):
    name = models.CharField(max_length=50)
    hex_value = models.CharField(max_length=7)  # Optional: HEX color code for display purposes

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=355, blank=True, null=True)
    image = models.FileField(upload_to='product_images/')  # Main image
    price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    on_sale = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    colors = models.ManyToManyField(Color, blank=True)  # Link to Color model
    sizes = models.ManyToManyField(Size, blank=True)    # Link to Size model
    ratings = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(5)])
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"



class OrderItem(models.Model):
    session_key = models.CharField(max_length=32)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.color}, {self.size})"

    def get_total_item_price(self):
        return self.quantity * self.product.price

class Order(models.Model):
    session_key = models.CharField(max_length=32)
    items = models.ManyToManyField(OrderItem)
    ordered = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(null=True)
    remark = models.CharField(max_length=255, blank=True, null=True, default="")

    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True, related_name='orders')
    
    user_details = models.ForeignKey(
    'UserDetails', on_delete=models.SET_NULL,blank=True, null=True )

    def __str__(self):
        return f"Order {self.pk}"

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()

        # Apply coupon if available
        if self.coupon and self.coupon.is_valid():
            discount = (self.coupon.percent_off / 100) * total
            total -= discount

        # if self.delivery_fee:
        #     total += self.delivery_fee.fee
        return total
    

    def get_sub_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()

        return total
    
    def get_total_quantity(self):
        quantity = 0
        for order_item in self.items.all():
            quantity += order_item.quantity

        return quantity
    



# class DeliveryFee(models.Model):
#     fee = models.FloatField(default=0.0)

#     def save(self, *args, **kwargs):
#         # Ensure only one row exists in the DeliveryFee model
#         if not self.pk and DeliveryFee.objects.exists():
#             # If a row exists, update it
#             existing_fee = DeliveryFee.objects.first()
#             existing_fee.fee = self.fee
#             existing_fee.save()
#             return existing_fee
#         return super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Delivery Fee: {self.fee}"


class Coupon(models.Model):
    code = models.CharField(max_length=15, unique=True)
    percent_off = models.PositiveIntegerField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    max_usage = models.PositiveIntegerField(default=1)
    usage_count = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        # Check if the coupon is active, within usage limits, and not expired
        return (self.active and
                (self.usage_count < self.max_usage) and
                (not self.expiry_date or self.expiry_date >= timezone.now().date()))
    

class UserDetails(models.Model):
    session_key = models.CharField(max_length=32)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    order_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    









class Contact(models.Model):

    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()


    def __str__(self):
        return self.name