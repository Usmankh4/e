from django.urls import path
from .views import get_products, get_product_detail, get_product_by_slug, home, get_brands, get_categories, get_phone_brands, get_phone_models, get_repair_services, get_accessories
from .stripe_views import create_checkout_session, create_buy_now_session, get_session_details
from .inventory_views import get_variant_stock, update_variant_stock, reserve_inventory, release_reservation, commit_reservation, validate_inventory, cleanup_expired_reservations
from .webhook_views import stripe_webhook
from .auth_views import (
    MyTokenObtainPairView, RegisterView, UserProfileView,
    logout_view, get_user_data
)
from .cart_views import (
    get_cart, add_to_cart, update_cart_item, remove_from_cart,
    merge_carts, clear_cart, validate_cart
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Home view
    path('', home, name='home'),
    
    # Product views
    path('api/products/', get_products, name='get_products'),
    path('api/products/<int:pk>/', get_product_detail, name='get_product_detail'),
    path('api/products/by-slug/<slug:slug>/', get_product_by_slug, name='get_product_by_slug'),
    path('api/brands/', get_brands, name='get_brands'),
    path('api/categories/', get_categories, name='get_categories'),
   
    # Phone repair views
    path('api/phone-brands/', get_phone_brands, name='get_phone_brands'),
    path('api/phone-models/<slug:brand_slug>/', get_phone_models, name='get_phone_models'),
    path('api/repair-services/<slug:model_slug>/', get_repair_services, name='get_repair_services'),
    path('api/accessories/', get_accessories, name='get_accessories'),
   
    # Inventory views
    path('api/inventory/variant/<int:variant_id>/', get_variant_stock, name='get_variant_stock'),
    path('api/inventory/variant/', get_variant_stock, name='get_variant_stock_filtered'),
    path('api/inventory/update/', update_variant_stock, name='update_variant_stock'),
    path('api/inventory/reserve/', reserve_inventory, name='reserve_inventory'),
    path('api/inventory/release/', release_reservation, name='release_reservation'),
    path('api/inventory/commit/', commit_reservation, name='commit_reservation'),
    path('api/inventory/validate/', validate_inventory, name='validate_inventory'),
    path('api/inventory/cleanup-expired/', cleanup_expired_reservations, name='cleanup_expired_reservations'),
   
    # Stripe views
    path('api/create-checkout-session/', create_checkout_session, name='create_checkout_session'),
    path('api/create-buy-now-session/', create_buy_now_session, name='create_buy_now_session'),
    path('api/get-session-details/', get_session_details, name='get_session_details'),
   
    # Webhook views
    path('webhook/', stripe_webhook, name='stripe_webhook'),
    
    # Authentication views
    path('api/auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/profile/', UserProfileView.as_view(), name='user_profile'),
    path('api/auth/logout/', logout_view, name='logout'),
    path('api/auth/user/', get_user_data, name='user_data'),
    
    # Cart views
    path('api/cart/', get_cart, name='get_cart'),
    path('api/cart/add/', add_to_cart, name='add_to_cart'),
    path('api/cart/update/<int:item_id>/', update_cart_item, name='update_cart_item'),
    path('api/cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('api/cart/merge/', merge_carts, name='merge_carts'),
    path('api/cart/clear/', clear_cart, name='clear_cart'),
    path('api/cart/validate/', validate_cart, name='validate_cart'),
]
