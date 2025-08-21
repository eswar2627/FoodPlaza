from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils import timezone
from customer.models import OrderModel


class Dashboard(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        # Get today's date
        today = timezone.now().date()

        # Fetch all orders placed today
        orders = OrderModel.objects.filter(created_on__date=today)

        # Filter out only unshipped orders
        unshipped_orders = [order for order in orders if not order.is_shipped]

        # Calculate total revenue (from all today's orders)
        total_revenue = sum(order.price for order in orders)

        context = {
            'orders': unshipped_orders,
            'total_revenue': total_revenue,
            'total_orders': len(orders)
        }

        return render(request, 'restaurant/dashboard.html', context)

    def test_func(self):
        return self.request.user.groups.filter(name='Staff').exists()


class OrderDetails(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, pk, *args, **kwargs):
        # Safely get the order by primary key or return 404
        order = get_object_or_404(OrderModel, pk=pk)

        context = {
            'order': order,
        }

        return render(request, 'restaurant/order_details.html', context)

    def post(self, request, pk, *args, **kwargs):
        # Mark the order as shipped
        order = get_object_or_404(OrderModel, pk=pk)
        order.is_shipped = True
        order.save()

        context = {
            'order': order,
        }

        return render(request, 'restaurant/order_details.html', context)

    def test_func(self):
        return self.request.user.groups.filter(name='Staff').exists()
