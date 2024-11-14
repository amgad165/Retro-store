from base.models import Order, OrderItem  # Import your Order and OrderItem models

def cart_details(request):
    if request.session.session_key:
        # Get the cart for the logged-in user
        session_key = request.session.session_key
        cart = Order.objects.filter(session_key=session_key, ordered=False).first()

        if cart:
            # Calculate the total number of items and their quantities in the cart
            total_quantity = cart.get_total_quantity()
            total_price = cart.get_total()
        else:
            total_quantity = 0
            total_price = 0

    else:
        total_quantity = 0
        total_price = 0

    return {'total_quantity': total_quantity, 'total_price': total_price}