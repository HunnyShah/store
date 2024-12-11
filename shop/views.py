from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, CartItem, Order, OrderItem, ProductReview
from .forms import ProductForm, UpdateQuantityForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Exists, OuterRef, Subquery
from django.db.models import Avg
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView

def is_admin(user):
    return user.is_staff

class CustomLoginView(LoginView):
    def get_success_url(self):
        return reverse_lazy('home')
    
def index(request):
    query = request.GET.get('q')  # Get the search query from the URL
    if query:
        products = Product.objects.filter(name__icontains=query)  # Search products by name
    else:
        products = Product.objects.all()  # Show all products if no query

    products = products.annotate(average_rating=Avg('reviews__star'))

    # Pass the products to the template
    return render(request, 'shop/homepage.html', {'products': products})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('home')  # Redirect to the index page
        else:
            messages.error(request, 'There was an error adding the product.')
    else:
        form = ProductForm()

    return render(request, 'shop/add_product.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'shop/profile.html', {'user': request.user})

def logout_done(request):
    return render(request, 'shop/logout_done.html')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get the user's cart or create a new one if it doesn't exist
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if the product is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        # If product already exists in cart, increment the quantity
        cart_item.quantity += 1
        cart_item.save()

    return redirect('home')

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def update_quantity(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    if request.method == 'POST':
        form = UpdateQuantityForm(request.POST, instance=cart_item)
        if form.is_valid():
            form.save()
            return redirect('cart')
    else:
        form = UpdateQuantityForm(instance=cart_item)
    return render(request, 'shop/update_quantity.html', {'form': form, 'cart_item': cart_item})

@login_required
def delete_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

@login_required
def search_cart(request):
    query = request.GET.get('q')
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    if query:
        cart_items = cart_items.filter(product__name__icontains=query)
    return render(request, 'shop/cart.html', {'cart_items': cart_items})

@login_required
def place_order(request):
    # Get the user's cart
    cart = request.user.cart
    cart_items = cart.cartitem_set.all()

    # Calculate the total price of the cart
    total_price = sum(item.get_total_price() for item in cart_items)

    # Create the order
    order = Order.objects.create(user=request.user, total_price=total_price)

    # Add cart items to the order as OrderItems
    order_items = []
    for cart_item in cart_items:
        order_item = OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity)
        order_items.append(order_item)

    # Clear the user's cart after placing the order
    cart_items.delete()

    # Redirect to the order history page
    return redirect('order_history')  # Change to your desired URL

# View for displaying order history
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-placed_at')
    return render(request, 'shop/order_history.html', {'orders': orders})

from django.db.models import Exists, OuterRef

@login_required
def order_details(request, id):
    order = get_object_or_404(Order, id=id)

    # Annotate each order item with whether the user has reviewed the product and its star rating
    order_items = order.order_items.annotate(
        has_review=Exists(
            ProductReview.objects.filter(product=OuterRef('product'), user=request.user)
        ),
        review_star=Subquery(
            ProductReview.objects.filter(
                product=OuterRef('product'),
                user=request.user
            ).values('star')[:1]  # Get the first result (if any)
        )
    )

    # Add reviews directly to the context for each order item
    order_item_data = []
    for item in order_items:
        review = ProductReview.objects.filter(product=item.product, user=request.user).first()
        order_item_data.append({
            "product": item.product,
            "quantity": item.quantity,
            "price": item.product.price,
            "total_price": item.get_total_price(),
            "has_review": bool(review),
            "review_star": review.star if review else "Not Rated",
        })

    return render(request, 'shop/order_details.html', {
        'order': order,
        'order_item_data': order_item_data,
    })

@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to the homepage after successful edit
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/edit_product.html', {'form': form, 'product': product})

@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('home')

@login_required
def product_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    review = ProductReview.objects.filter(product=product, user=request.user).first()

    if request.method == "POST":
        star_rating = request.POST.get('star')
        # Update or create the review
        review, created = ProductReview.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={'star': star_rating}
        )
        order_item = OrderItem.objects.filter(product=product, order__user=request.user).first()
        if order_item:
            order_id = order_item.order.id
            return redirect('order_details', id=order_id)


    return render(request, 'shop/product_review.html', {
        'product': product,
        'review': review,
        'star_range': [i for i in range(1, 6)]  # Pass the range for 1-5 stars
    })