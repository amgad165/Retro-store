from django.contrib import admin
from .models import *
from .forms import ProductImageForm
# Register your models here.

admin.site.register(Category)
admin.site.register(Section)
# admin.site.register(Product)

admin.site.register(Color)
admin.site.register(Size)




class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Shows one empty form for new uploads

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

    def save_related(self, request, obj, form, change):
        super().save_related(request, obj, form, change)
        if 'images' in request.FILES:
            for image in request.FILES.getlist('images'):
                ProductImage.objects.create(product=obj, image=image)

admin.site.register(Product, ProductAdmin)


admin.site.register(OrderItem)

from django.contrib import admin
from .models import Order, OrderItem, Product, Color, Size, Coupon, UserDetails

from django.contrib import admin
from .models import Order, OrderItem, Product, Color, Size, Coupon, UserDetails

class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_summary', 'get_user_name', 'get_user_phone', 
        'get_user_email', 'get_user_address', 'get_order_total', 'get_order_quantity', 
        'get_subtotal', 'get_discount', 'ordered_date', 'ordered', 'delivered', 'received'
    )
    list_editable = ('delivered', 'received')  # Make being_delivered and received editable
    search_fields = ('order_summary',)  # Allow searching by order summary
    list_filter = ('ordered', 'delivered')  # Filters for ordered and being_delivered fields
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('-ordered', 'delivered')

    def order_summary(self, obj):
        # Generate a summary of items in the order (quantity x product name)
        return ", ".join([str(item) for item in obj.items.all()])
    order_summary.short_description = 'Order'

    def get_user_name(self, obj):
        # Get user's full name from UserDetails
        return f"{obj.user_details.first_name} {obj.user_details.last_name}" if obj.user_details else ""
    get_user_name.short_description = 'Name'

    def get_user_phone(self, obj):
        # Get user's phone from UserDetails
        return obj.user_details.phone if obj.user_details else ""
    get_user_phone.short_description = 'Phone'

    def get_user_email(self, obj):
        # Get user's email from UserDetails
        return obj.user_details.email if obj.user_details else ""
    get_user_email.short_description = 'Email'

    def get_user_address(self, obj):
        # Get user's full address from UserDetails
        if obj.user_details:
            address = obj.user_details.address
            city = obj.user_details.city
            country = obj.user_details.country
            if obj.user_details.apartment:
                apartment = obj.user_details.apartment
                full_address = f" {address},{apartment} , '\n' {city}, {country}"

            else:
                full_address = f" {address} , '\n' {city}, {country}"

            # Concatenate the address fields
            return full_address
        return ""
    get_user_address.short_description = 'Address'

    def get_order_total(self, obj):
        # Get total amount for the order, applying any coupon discounts
        total = obj.get_total()  # Assuming the get_total method handles total calculation
        return f"{total:.2f} EGP"  # Format the total as currency
    get_order_total.short_description = 'Total'

    def get_order_quantity(self, obj):
        # Get the total quantity of items in the order
        return obj.get_total_quantity()  # Assuming get_total_quantity method exists
    get_order_quantity.short_description = 'Total qty'

    def get_subtotal(self, obj):
        # Get the subtotal of the order (before discounts)
        return f"{obj.get_sub_total():.2f} EGP"  # Assuming get_subtotal method exists
    get_subtotal.short_description = 'Subtotal'

    def get_discount(self, obj):
        # Get discount applied to the order
        if obj.coupon:
            discount = obj.coupon.percent_off  # Assuming get_discount method exists
        else:   
            discount = 0
        return f"{discount:.2f} %"  # Format the discount as percentage
    get_discount.short_description = 'Discount'

    def ordered_date(self, obj):
        # Display the order's ordered date
        return obj.ordered_date
    ordered_date.short_description = 'Ordered Date'

admin.site.register(Order, OrderAdmin)






admin.site.register(UserDetails)

admin.site.register(Coupon)
admin.site.register(Contact)
