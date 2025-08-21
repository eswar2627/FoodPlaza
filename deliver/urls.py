from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from customer import views
from django.conf.urls.static import static
from django.urls import path, include
from customer.views import (
    IndexView, AboutView, RegisterView, LoginView, LogoutView,
    OrderView, PaymentMethodView, OrderConfirmationView, MenuSearch, Menu, download_invoice,OrderTrackView,OrderHistoryView,SalesReportView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('restaurant/', include('restaurant.urls')),

    # Customer pages
    path('', IndexView.as_view(), name='index'),
    path('about/', AboutView.as_view(), name='about'),
    path('menu/search/', MenuSearch.as_view(), name='menu-search'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('menu/', Menu.as_view(), name='menu'),
    path('profile/', views.profile_view, name='profile'),

    # Order related
    path('order/', OrderView.as_view(), name='order'),
    path('payment-methods/', PaymentMethodView.as_view(), name='payment-methods'),
    path('order-confirmation/<int:pk>/', OrderConfirmationView.as_view(), name='order-confirmation'),
    path('download-invoice/<int:order_id>/', download_invoice, name='download-invoice'),  # ✅ Added this line
    path('track-order/<int:pk>/', OrderTrackView.as_view(), name='track-order'),
    path('order-history/', OrderHistoryView.as_view(), name='order-history'),
    path('admin/sales-report/', SalesReportView.as_view(), name='sales-report'),
    path('admin/sales-report/', SalesReportView.as_view(), name='sales-report'),
    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
