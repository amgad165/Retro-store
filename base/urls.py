from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('shop', views.shop, name='shop'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.cart, name='cart'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('remove_item/<int:item_id>/', views.remove_item, name='remove_item'),
    path('confirm_order/', views.confirm_order, name='confirm_order'),
    path('contacts/', views.contacts, name='contacts'),
    path('my_orders/', views.my_orders, name='my_orders'),

    path('calculate-price/', views.calculate_price, name='calculate_price'),


]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
