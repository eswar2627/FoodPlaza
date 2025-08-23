from django.urls import path
from django.contrib.auth.views import LoginView
from .views import Dashboard, OrderDetails

urlpatterns = [
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('order/<int:pk>/', OrderDetails.as_view(), name='order-details'),
    path('orders/<int:pk>/', OrderDetails.as_view()),

    # Optional: restaurant login (if you're using that)
    path('restaurant/login/', LoginView.as_view(template_name='restaurant/login.html'), name='restaurant-login'),
]
