from itertools import count
from django.http import HttpResponseServerError, JsonResponse
from django.shortcuts import render
from .models import *
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Min, Max
from django.db.models import Count, Min, Max, Q
from django.core.paginator import Paginator

# Create your views here.

def index(request):
    sections = Section.objects.all()
    
    # Create a dictionary to store sections and their associated products
    sections_with_products = {
        section: Product.objects.filter(section=section) for section in sections
    }
    
    # Pass sections_with_products to the template
    context = {'sections_with_products': sections_with_products}
    return render(request, 'index.html', context)



def shop(request):
    # Get all products
    products = Product.objects.all().order_by('-id')

    # Get filter options
    categories = Category.objects.annotate(product_count=Count('product'))
    price_aggregate = products.aggregate(min_price=Min('price'), max_price=Max('price'))
    min_price = price_aggregate['min_price'] if price_aggregate['min_price'] is not None else 0
    max_price = price_aggregate['max_price'] if price_aggregate['max_price'] is not None else 0

    # Retrieve filter parameters from the request
    category_id = request.GET.get('category')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    search_query = request.GET.get('search', '')  # New search parameter

    # Apply filters
    if category_id:
        products = products.filter(category_id=category_id)
    if price_min and price_max:
        products = products.filter(price__gte=price_min, price__lte=price_max)
    if search_query:
        products = products.filter(Q(name__icontains=search_query) )

    # Pagination
    paginator = Paginator(products, 8)  # Show 8 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Total count of filtered products
    total_products_count = products.count()

    context = {
        'products': page_obj,              # Paginated product list
        'categories': categories,           # Categories with product count
        'min_price': min_price,
        'max_price': max_price,
        'search_query': search_query,       # Pass search query to the template
        'total_products_count': total_products_count,  # Total count for display
    }
    return render(request, 'shop.html', context)








def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {'product': product}
    return render(request, 'shop-details.html', context)


def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('id')
        qty = int(request.POST.get('qty', 1))
        size_id = request.POST.get('size')
        color_id = request.POST.get('color')

        product = get_object_or_404(Product, pk=product_id)
        
        # Retrieve color and size objects if provided
        color = get_object_or_404(Color, pk=color_id) if color_id else None
        size = get_object_or_404(Size, pk=size_id) if size_id else None

        # Use session key to identify the cart for the user
        session_key = request.session.session_key
        if not session_key:
            request.session.cycle_key()
            session_key = request.session.session_key

        # Create or get the order item with color and size
        order_item, created = OrderItem.objects.get_or_create(
            session_key=session_key,
            product=product,
            color=color,
            size=size,
            ordered=False,
            defaults={'quantity': qty}
        )

        # Update the quantity if the item already exists
        if not created:
            order_item.quantity += qty
            order_item.save()

        # Check if an order exists for the user's session
        order_qs = Order.objects.filter(session_key=session_key, ordered=False)
        if order_qs.exists():
            order = order_qs.first()
            if not order.items.filter(id=order_item.id).exists():
                order.items.add(order_item)
        else:
            # Create a new order for the user's session
            ordered_date = timezone.now()
            order = Order.objects.create(session_key=session_key, ordered_date=ordered_date)
            order.items.add(order_item)

        # Calculate total quantity and price for the cart
        cart_items = order.items.all()
        total_quantity = sum(item.quantity for item in cart_items)
        total_price = sum(item.get_total_item_price() for item in cart_items)

        return JsonResponse({'success': 'Item added to cart', 'cart_products_count': total_quantity, 'total_price': total_price})

    return JsonResponse({'error': 'Invalid request'})

def checkout(request):
    session_key = request.session.session_key  # Get the currently logged-in session user
    try:
        order = Order.objects.get(session_key=session_key, ordered=False)
        order_items = order.items.all()
        cart_count = len(order.items.all())
        
        # get total orders 
        total_price = order.get_total()
        subtotal_price = order.get_sub_total()

        if order.coupon:
            discount= order.coupon.percent_off
        else:
            discount = None

        # if order.delivery_fee:
        #     delivery_fee= order.delivery_fee.fee
        # else:
        #     delivery_fee = None

        delivery_fee = None


        return render(request, "checkout.html", {'order_items': order_items,'total_price':total_price,'subtotal_price':subtotal_price,"cart_count":cart_count , "discount":discount,"order":order,"delivery_fee":delivery_fee})

    except Order.DoesNotExist:
        # Handle the case where the order doesn't exist
        order_items = None    
        return render(request, "checkout.html", {'order_items': order_items})



def cart(request):
    session_key = request.session.session_key  # Get the currently logged-in session user
    try:
        order = Order.objects.get(session_key=session_key, ordered=False)
        order_items = order.items.all()
        cart_count = len(order.items.all())
        
        # get total orders 
        total_price = order.get_total()
        sub_total = order.get_sub_total()

        if order.coupon:
            discount= order.coupon.percent_off
        else:
            discount = None

        # if order.delivery_fee:
        #     delivery_fee= order.delivery_fee.fee
        # else:
        #     delivery_fee = None


        # return render(request, "cart.html", {'order_items': order_items,'total_price':total_price,"cart_count":cart_count,"discount":discount,"delivery_fee":delivery_fee})
        return render(request, "cart.html", {'order_items': order_items,'total_price':total_price,"cart_count":cart_count,"sub_total":sub_total,"discount":discount})

    except Order.DoesNotExist:
        # Handle the case where the order doesn't exist
        order_items = None    
        return render(request, "cart.html", {'order_items': order_items})
    

def update_cart(request):
    print('hha')
    if request.method == "POST":
        # Process the data sent by the "Update Cart" button

        item_ids = request.POST.getlist('item_id')
        quantities = request.POST.getlist('quantity')  # These are the updated quantities

        print(item_ids)
        print(quantities)
        session_key = request.session.session_key
        # Loop through the product IDs and quantities to update the cart
        for item_id, quantity in zip(item_ids, quantities):
            quantity = int(quantity)  # Convert the quantity to an integer

            cart = OrderItem.objects.get(id=item_id)
            cart.quantity = quantity
            
            cart.save()
        
        # Return a JSON response to indicate success (you can customize this)
        
        return redirect("cart")

    # Handle GET requests (if needed)
    return JsonResponse({"message": "Invalid request"}, status=400)
    
def remove_item(request,item_id):
    if request.method == "GET":
        item_id = item_id
        session_key = request.session.session_key 
        
        # Delete the OrderItem
        order_item = OrderItem.objects.get(
            id=item_id,
        )
        
        if order_item:
            order_item.delete()
        
        
        # Return the updated total price as JSON response
        return redirect("cart")
        
    return JsonResponse({'message': 'Invalid request'}, status=400)


def confirm_order(request):
    if request.method == 'POST':
        session_key = request.session.session_key

        try:
            # Retrieve the existing order for the session
            order = Order.objects.get(session_key=session_key, ordered=False)
            order_items = order.items.all()
            
            # Collect user details from the POST request
            user_details, created = UserDetails.objects.update_or_create(
                session_key=session_key,
                defaults={
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'country': request.POST.get('country'),
                'address': request.POST.get('address'),
                'apartment': request.POST.get('apartment', ''),
                'city': request.POST.get('city'),
                'phone': request.POST.get('phone'),
                'email': request.POST.get('email'),
                'order_notes': request.POST.get('order_notes', '')
                }
            )
            
            # Mark order items as ordered
            order_items.update(ordered=True)
            order.ordered = True
            order.user_details = user_details
            order.save()

            return render(request, "success.html")  # Success page after order confirmation

        except Exception as e:
            return HttpResponseServerError("A serious error occurred. We have been notified.", content_type="text/plain")
    
    return HttpResponseServerError("Invalid request method", content_type="text/plain")

def calculate_price(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '')

        # Get the user's current order
        try:
            session_key = request.session.session_key  # Get the currently logged-in session user
            order = Order.objects.get(session_key=session_key, ordered=False)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'No active order found'}, status=404)



        # Attach coupon if provided
        coupon_message = ''

        if order.coupon :
            if order.coupon.is_valid():
                coupon_message = f"Discount applied: {order.coupon.percent_off}%"

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.is_valid():
                    order.coupon = coupon
                    coupon.usage_count += 1
                    coupon.save()
                    order.save()
                    coupon_message = f"Discount applied: {coupon.percent_off}%"
                else:
                    coupon_message = "Discount code invalid or expired."
            except Coupon.DoesNotExist:
                coupon_message = "Please enter a valid discount code."


        # Calculate the final price with the new `get_final_total` method
        final_price = order.get_total()
        

        # Response messages for clarity
        response_message = {
            'coupon_message': coupon_message,
        }

        print(final_price)

        return JsonResponse({
            'final_price': f"{final_price:.2f}",
            'messages': response_message
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)



def contacts(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Create and save the contact instance
        contact = Contact(
            name=name,
            email=email,
            message=message
        )
        contact.save()

        # Redirect to a success page
        return redirect('index')
    return render(request, 'contacts.html')






def submit_contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        message = request.POST.get('message')
        
        # Create and save the contact instance
        contact = Contact(
            name=name,
            email=email,
            telephone_number=phone,
            address = address,
            message=message
        )
        contact.save()

        # Redirect to a success page
        return redirect('success_contact')
    
    return render(request, 'index.html')  # If not POST, render the index page again








def my_orders(request):
    session_key = request.session.session_key
    orders = Order.objects.filter(session_key=session_key, ordered=True)
    return render(request, 'my_orders.html', {'orders': orders})