# views.py (with full support for order tracking timeline + Chart.js in sales report)
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from django.db.models import Q, Sum, Count
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from weasyprint import HTML
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import MenuItem, OrderModel
from .form import RegisterForm
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView

# ---------- Homepage ----------
class IndexView(View):
    def get(self, request):
        return render(request, 'customer/index.html')


# ---------- About Page ----------
class AboutView(View):
    def get(self, request):
        return render(request, 'customer/about.html')


# ---------- Register ----------
class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'customer/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
        return render(request, 'customer/register.html', {'form': form})


# ---------- Login ----------
class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'customer/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('index')
        messages.error(request, 'Invalid username or password.')
        return render(request, 'customer/login.html', {'form': form})


# ---------- Logout ----------
class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect('login')


# ---------- Order View ----------
@method_decorator(login_required, name='dispatch')
class OrderView(View):
    def get(self, request):
        context = {
            'appetizers': MenuItem.objects.filter(category__name__icontains='Appetizer'),
            'starters': MenuItem.objects.filter(category__name__icontains='Starter'),
            'drinks': MenuItem.objects.filter(category__name__icontains='Drink'),
            'juices': MenuItem.objects.filter(category__name__icontains='Juice'),
            'desserts': MenuItem.objects.filter(category__name__icontains='Dessert'),
        }
        return render(request, 'customer/order.html', context)

    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zip')
        payment_method = request.POST.get('payment_method')
        items = request.POST.getlist('items')

        order_items = {'items': []}
        for item in items:
            menu_item = MenuItem.objects.get(pk=int(item))
            order_items['items'].append({
                'id': menu_item.pk,
                'name': menu_item.name,
                'price': menu_item.price
            })

        price = sum(item['price'] for item in order_items['items'])
        item_ids = [item['id'] for item in order_items['items']]

        order = OrderModel.objects.create(
            user=request.user,
            price=price,
            name=name,
            email=email,
            street=street,
            city=city,
            state=state,
            zipcode=zipcode,
            payment_method=payment_method,
            status='Confirmed',
            is_paid=True,
            is_shipped=False
        )
        order.items.add(*item_ids)
        order.save()

        send_order_confirmation_email(order)

        request.session['order_id'] = order.pk
        return redirect('payment-methods')


@method_decorator(staff_member_required, name='dispatch')
class SalesReportView(TemplateView):
    template_name = 'admin/sales_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = OrderModel.objects.all()

        context['total_orders'] = orders.count()
        context['total_sales'] = orders.aggregate(Sum('price'))['price__sum'] or 0
        context['status_breakdown'] = orders.values('status').annotate(count=Count('id'))
        context['daily_sales'] = orders.extra({'date': "date(created_on)"}).values('date').annotate(total=Sum('price')).order_by('date')
        context['payment_data'] = orders.values('payment_method').annotate(count=Count('id'))  # Added pie chart data
        context['payment_data'] = orders.values('payment_method').annotate(count=Count('id'))
        return context


# ---------- Payment Methods ----------
@method_decorator(login_required, name='dispatch')
class PaymentMethodView(View):
    def get(self, request):
        order_id = request.session.get('order_id')
        if not order_id:
            return redirect('order')
        order = get_object_or_404(OrderModel, pk=order_id, user=request.user)
        return render(request, 'customer/payment_methods.html', {'order': order})


# ---------- Menu View ----------
class Menu(View):
    def get(self, request):
        menu_items = MenuItem.objects.all()
        return render(request, 'customer/menu.html', {'menu_items': menu_items})


# ---------- Menu Search ----------
class MenuSearch(View):
    def get(self, request):
        query = self.request.GET.get("q")
        menu_items = MenuItem.objects.filter(
            Q(name__icontains=query) |
            Q(price__icontains=query) |
            Q(description__icontains=query)
        )
        return render(request, 'customer/menu.html', {'menu_items': menu_items})


# ---------- Send Invoice Email with PDF ----------
def send_order_confirmation_email(order):
    subject = f"Your Order Confirmation - Order #{order.pk}"
    to_email = order.email

    html_message = render_to_string('customer/email_invoice.html', {
        'order': order,
        'items': order.items.all(),
    })

    pdf_file = HTML(string=html_message).write_pdf()

    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email]
    )
    email.content_subtype = 'html'
    email.attach(f"invoice_order_{order.pk}.pdf", pdf_file, 'application/pdf')
    email.send()


# ---------- Download Invoice View ----------
@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(OrderModel, pk=order_id, user=request.user)
    items = order.items.all()

    html_string = render_to_string('customer/email_invoice.html', {
        'order': order,
        'items': items
    })

    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_order_{order.id}.pdf"'
    response.write(pdf)
    return response


# ---------- Order Confirmation Page ----------
class OrderConfirmationView(View):
    def get(self, request, pk):
        order = get_object_or_404(OrderModel, pk=pk, user=request.user)
        items = order.items.all()
        price = order.price
        return render(request, 'customer/order_confirmation.html', {
            'order': order,
            'items': items,
            'price': price
        })

class OrderHistoryView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get(self, request):
        orders = OrderModel.objects.filter(user=request.user).order_by('-created_on')
        return render(request, 'customer/order_history.html', {'orders': orders})

class YourViewName(LoginRequiredMixin, View):
    def post(self, request):
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # Save to order or whatever model you're working with
        order = OrderModel.objects.filter(user=request.user).last()
        if order:
            order.latitude = latitude
            order.longitude = longitude
            order.save()

        return redirect('some-view-name')  # or render a response


# ---------- Template Filter for Timeline ----------
from django import template
register = template.Library()

@register.filter
def is_step_active(current_status, step):
    order_statuses = ['Pending', 'Confirmed', 'Preparing', 'Out for Delivery', 'Delivered']
    try:
        return order_statuses.index(step) <= order_statuses.index(current_status)
    except ValueError:
        return False


@method_decorator(login_required, name='dispatch')
class OrderTrackView(View):
    def get(self, request, pk):
        order = get_object_or_404(OrderModel, pk=pk, user=request.user)
        steps = ['Pending', 'Confirmed', 'Preparing', 'Out for Delivery', 'Delivered']
        return render(request, 'customer/track_order.html', {
            'order': order,
            'steps': steps
        })

@login_required
def profile_view(request):
    return render(request, 'customer/profile.html')