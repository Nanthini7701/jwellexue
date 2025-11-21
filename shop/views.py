from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from .models import Product, Category, CartItem, WishlistItem, Order
from .forms import SignUpForm
import razorpay
from django.contrib.auth.models import User
import random
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import login, authenticate, logout
def index(request):
    q = request.GET.get('q', '')
    cat = request.GET.get('category', '')
    metal = request.GET.get('metal', '')
    
    products = Product.objects.filter(available=True)

    if q:
        products = products.filter(name__icontains=q)
    if cat:
        products = products.filter(category__slug=cat)
    if metal:
        products = products.filter(metal_type__iexact=metal)

    categories = Category.objects.all()
    metals = Product.objects.values_list('metal_type', flat=True).distinct()

    return render(request, 'shop/index.html', {
        'products': products,
        'categories': categories,
        'q': q,
        'metals': metals,
        'request': request
    })
def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'shop/detail.html', {'product': product})
def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        send_mail(
            subject or "New Contact Message",
            f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        messages.success(request, "Your message has been sent successfully!")
        return redirect("contact")

    return render(request, "shop/contact.html")
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "Email does not exist!")
            return redirect("shop:forgot_password")

        otp = random.randint(100000, 999999)
        request.session['reset_email'] = email
        request.session['reset_otp'] = otp

        send_mail(
            "Your OTP to Reset Password",
            f"Your OTP is {otp}. Do not share it with anyone.",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False
        )

        messages.success(request, "OTP sent to your email!")
        return redirect("shop:verify_otp")

    return render(request, "shop/forgot_password.html")

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        saved_otp = str(request.session.get("reset_otp"))

        if entered_otp == saved_otp:
            return redirect("shop:reset_password")
        else:
            messages.error(request, "Invalid OTP")
            return redirect("shop:verify_otp")

    return render(request, "shop/verify_otp.html")

def reset_password(request):
    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("shop:reset_password")

        email = request.session.get("reset_email")
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        # clear session
        request.session.flush()

        messages.success(request, "Password changed successfully! Login now.")
        return redirect("shop:login")

    return render(request, "shop/reset_password.html")
def signup_view(request):
    """
    Recommended behavior: create user, auto-login, redirect to index.
    If you prefer user to login manually, see alternative below.
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get("email")
            user.save()

            # Option A: AUTO LOGIN (recommended)
            login(request, user)
            messages.success(request, f"Signup successful — welcome, {user.username}!")
            return redirect("shop:index")

            # ----- Option B: Redirect to login (uncomment if you prefer)
            # messages.success(request, "Account created. Please log in.")
            # return redirect("shop:login")
        else:
            # form invalid -> errors will show in template
            messages.error(request, "Please fix the errors below.")
    else:
        form = SignUpForm()

    return render(request, "shop/signup.html", {"form": form})
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("shop:index")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "shop/login.html")
def logout_view(request):
    if request.method == "POST":   # prevents 405 error
        logout(request)
        return redirect("shop:index")
    return redirect("shop:index")
# ---------------- CART ----------------

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, available=True)
    obj, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.quantity += 1
        obj.save()
    return redirect('shop:cart')

def logout_success(request):
    return render(request, 'shop/logout_success.html')
@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(CartItem, pk=pk, user=request.user)
    item.delete()
    return redirect('shop:cart')


@login_required
def update_cart_quantity(request, pk):
    if request.method == "POST":
        item = CartItem.objects.get(pk=pk)
        qty = int(request.POST.get("quantity", 1))
        item.quantity = qty
        item.save()
        return redirect('shop:index')  
@login_required
def cart(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum([i.line_total() for i in items])
    return render(request, 'shop/cart.html', {'items': items, 'total': total})


# ---------------- WISHLIST ----------------

@login_required
def add_to_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk, available=True)
    WishlistItem.objects.get_or_create(user=request.user, product=product)
    return redirect('shop:wishlist')


@login_required
def remove_from_wishlist(request, pk):
    item = get_object_or_404(WishlistItem, pk=pk, user=request.user)
    item.delete()
    return redirect('shop:wishlist')


@login_required
def wishlist(request):
    items = WishlistItem.objects.filter(user=request.user)
    return render(request, 'shop/wishlist.html', {'items': items})


# ---------------- CHECKOUT / RAZORPAY ----------------

@login_required
def checkout(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum([i.line_total() for i in items])

    if total <= 0:
        return redirect('shop:cart')

    order = Order.objects.create(user=request.user, total=total)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    razor_order = client.order.create({
        "amount": int(total * 100),
        "currency": "INR",
        "payment_capture": "0"
    })

    order.razorpay_order_id = razor_order['id']
    order.save()

    return render(request, 'shop/checkout.html', {
        'order': order,
        'razorpay_order': razor_order,
        'total': total,
        'razorpay_key': settings.RAZORPAY_KEY_ID
    })


@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_signature = request.POST.get("razorpay_signature")

        # (Optional) verify signature using Razorpay client
        # If everything is fine → show success page
        
        return render(request, "shop/payment_success.html")

    return redirect("shop:index")