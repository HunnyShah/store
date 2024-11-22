from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='logout_done'), name='logout'),
    path('logout/done/', views.logout_done, name='logout_done'),  # Redirect to the logout page after logging out,
    path('register/', views.register, name='register'),
    path('', views.index, name='home'),
    path('add/', views.add_product, name='add_product'),  # The add product page
    path('accounts/profile/', views.profile_view, name='profile'),
    path('cart/', views.cart_view, name='cart'),
     path('cart/update/<int:cart_item_id>/', views.update_quantity, name='update_quantity'),
    path('cart/delete/<int:cart_item_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('cart/search/', views.search_cart, name='search_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
     path('place_order/', views.place_order, name='place_order'),
    path('order_history/', views.order_history, name='order_history'),
    path('order-details/<int:id>/', views.order_details, name='order_details'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
]
