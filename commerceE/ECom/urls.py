from ECom import views
from django.urls import path

from commerceE import settings
from django.conf.urls.static import static



urlpatterns = [
    path("", views.index, name="Index"),
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),


    path("shop", views.shop, name="shop"),
    path("shop-product", views.shopProduct, name="shop-product"),
    path("profile", views.profile, name= "profile"),
    path("address", views.address, name= "address"),
    path("cart", views.cart, name="cart"),
    path("checkout", views.checkout, name="checkout"),
    path("order-placed", views.order, name="order-placed"),
    path("track-orders", views.trackOrder, name="track-orders"),


    path("AuthHome", views.AuthHome, name="AuthHome"),
    path("Admin-add-product", views.AdminAddProduct, name="Admin-add-product"),
    path("Add-category", views.AddCategory, name="AddCategory"),
    path("view-category", views.viewCategory, name="view-category"),
    path("Admin-all-products", views.AdAllProduct, name="Admin-all-products"),
    path("Add-logout", views.logout_view, name="Add-logout"),
    path("Admin-home-product", views.AdminSiteHome, name = "Admin-home-product"),



    path("invoice", views.generate_invoice, name="invoice"),
    
    #json
    path("fetchProduct-one", views.productOne, name="fetchProduct-one")

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
