from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

from .models import Category, Product, CartItem, Order, Feedback, OrderItem
from .forms import FeedbackForm, AddressForm


# 🏠 Home
def home(request):
    categories = Category.objects.all()
    return render(request, 'shop/home.html', {'categories': categories})


# 📂 Category Products
def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = category.products.all()
    return render(request, 'shop/category_products.html', {
        'category': category,
        'products': products
    })


# 📦 Product Detail + Feedback
@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    feedbacks = Feedback.objects.filter(
        product=product).order_by('-created_at')

    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            Feedback.objects.create(
                product=product,
                user=request.user,
                rating=form.cleaned_data['rating'],
                comment=form.cleaned_data['comment']
            )
            messages.success(request, "Feedback added successfully!")
            return redirect('product_detail', product_id=product.id)
    else:
        form = FeedbackForm()

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'feedbacks': feedbacks,
        'form': form
    })


# 🛒 Add to Cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except:
        quantity = 1

    cart_item, created = CartItem.objects.get_or_create(
        product=product,
        user=request.user
    )

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()
    messages.success(request, f"{product.name} added to cart!")
    return redirect('cart')


# 🧾 Cart
@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)

    total_price = sum(
        item.product.price * item.quantity for item in cart_items
    )

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


# 💳 Checkout
@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('cart')

    total_price = sum(
        item.product.price * item.quantity for item in cart_items
    )

    if request.method == 'POST':
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.cleaned_data['address']
            payment_method = form.cleaned_data['payment_method']

            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                address=address,
                payment_method=payment_method
            )

            # Save order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            cart_items.delete()

            if payment_method == 'ONLINE':
                return redirect('payment_page', order_id=order.order_id)

            messages.success(request, f"Order placed! ID: {order.order_id}")
            return redirect('order_success', order_id=order.order_id)

    else:
        form = AddressForm()

    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'form': form,
        'total_price': total_price
    })


# 💰 Simulated Payment
@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    if request.method == 'POST':
        messages.success(request, "Payment successful!")
        return redirect('order_success', order_id=order.order_id)

    return render(request, 'shop/payment.html', {'order': order})


# ✅ Order Success
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'shop/order_success.html', {'order': order})


# 📦 Order History
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_history.html', {'orders': orders})


# 🔍 Order Detail
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})


# ❌ Cancel Order
@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    if order.status in ['Pending', 'Processing']:
        order.status = 'Cancelled'
        order.save()
        messages.success(request, "Order cancelled successfully.")
    else:
        messages.warning(request, "This order cannot be cancelled.")

    return redirect('order_history')


# 📄 DOWNLOAD PDF INVOICE (NEW)
@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    template = get_template('shop/invoice_pdf.html')
    html = template.render({'order': order})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response


# 📝 Register
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'shop/register.html', {'form': form})


# 🔐 Login
def user_login(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'shop/login.html')


# 🚪 Logout
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')
