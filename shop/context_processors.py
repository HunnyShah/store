from .models import Cart, CartItem

def cart_item_count(request):
    total_items = 0

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        total_items = sum(item.quantity for item in cart_items)

    return {'total_items': total_items}
