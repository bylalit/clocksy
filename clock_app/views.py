from django.shortcuts import get_object_or_404, render, redirect
from .models import Category, Product, Brand, Wishlist, Cart, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.

def index(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.all()[:8]
    wishlist_ids = []
    
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)
    return render(request, 'index.html', {'categories': categories, 'products': products, 'brands': brands, 'wishlist_ids': wishlist_ids})



def category(request, name):
    categories = Category.objects.all()

    category = get_object_or_404(Category, name=name)

    # Logged in user ki wishlist
    wishlist_ids = []

    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    # Sorting
    sort_order = request.GET.get('sort')

    if sort_order == "low":
        products = category.products.all().order_by('price')

    elif sort_order == "high":
        products = category.products.all().order_by('-price')

    else:
        products = category.products.all()

    brands = Brand.objects.all()

    context = {
        'categories': categories,
        'products': products,
        'brands': brands,
        'name': name,
        'wishlist_ids': wishlist_ids,
    }

    return render(request, 'category.html', context)


def singal_product(request, product_id):
    categories = Category.objects.all()
    product = Product.objects.get(id=product_id)
    brands = Brand.objects.all()
    # releted product
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)
        
    related_product = Product.objects.filter(category=product.category)[:8]
    return render(request, 'singal_product.html', {'categories': categories, 'products': product, 'related_products': related_product, 'brands': brands, 'wishlist_ids': wishlist_ids})


@login_required(login_url='/login')
def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_view')
    # return redirect(request.META.get("HTTP_REFERER", "index"))


@login_required(login_url='/login')
def cart_view(request):

    cart = Cart.objects.filter(user=request.user)

    total_amount = sum(
        item.product.price * item.quantity
        for item in cart
    )

    categories = Category.objects.all()
    brands = Brand.objects.all()

    context = {
        'cart': cart,
        'categories': categories,
        'brands': brands,
        'total_amount': total_amount,
    }

    return render(request, 'cart.html', context)


@login_required(login_url='/login')
def update_cart(request, product_id, action):

    try:
        cart_item = Cart.objects.get(
            user=request.user,
            product_id=product_id
        )

        if action == "increase":
            cart_item.quantity += 1
            cart_item.save()

        elif action == "decrease":

            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()

    except Cart.DoesNotExist:
        pass

    return redirect("cart_view")

@login_required(login_url='/login')
def remove_from_cart(request, product_id):

    Cart.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()

    return redirect("cart_view")


def category_brand(request, name, brand):
    categories = Category.objects.all()
    category = Category.objects.get(name=name)
    brand1 = Brand.objects.get(name=brand)
    products = Product.objects.filter(category=category, brand=brand1)
    brand = Brand.objects.all()
    return render(request, 'category.html', {'categories': categories,'products': products, 'brands': brand, 'name': name})

def category_brand_only(request, brand):
    categories = Category.objects.all()
    brand1 = Brand.objects.get(name=brand)
    products = Product.objects.filter(brand=brand1)
    brand = Brand.objects.all()
    return render(request, 'brand_product.html', {'categories': categories,'products': products, 'brands': brand, 'name': brand})


def search_page(request):
    data = request.POST.get('search')
    results = Product.objects.filter(name__icontains=data)
    categories = Category.objects.all()
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)
    return render(request, 'search_page.html', {'categories': categories, 'results': results, 'wishlist_ids': wishlist_ids})


def category_brand_only(request, brand):
    categories = Category.objects.all()
    brand = Brand.objects.all()
    brand1 = Brand.objects.get(name=brand)
    products = Product.objects.filter(brand=brand1)
    return render(request, 'brand_product.html', {'categories': categories,'products': products, 'brands': brand, 'name': brand})



def register(request):
    categories = Category.objects.all()
    brand = Brand.objects.all()
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username Already Exists")
            return redirect(register)
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Exists")
            return redirect(register)
            
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
        user.save()
        
        messages.success(request, "Account Created Successfully, Please Loged In.")
        return redirect(login_user)
        
    return render(request, 'register.html', {'categories': categories, 'brands': brand})


def login_user(request):
    categories = Category.objects.all()
    brand = Brand.objects.all()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect(index)
        else:
            messages.error(request, "Invalid username or Password!")
            return redirect(login_user)
        
    return render(request, 'login.html', {'categories': categories, 'brands': brand})

def logout_user(request):
    logout(request)
    return redirect(index)

def account(request):
    categories = Category.objects.all()
    brand = Brand.objects.all()
    return render(request, 'account.html', {'user': request.user,'categories': categories, 'brands': brand})



@login_required(login_url="/login")
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    )

    if wishlist_item.exists():
        wishlist_item.delete()
    else:
        Wishlist.objects.create(
            user=request.user,
            product=product
        )

    return redirect(request.META.get("HTTP_REFERER", "index"))

@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user)

    categories = Category.objects.all()
    brands = Brand.objects.all()

    context = {
        'wishlist': wishlist,
        'categories': categories,
        'brands': brands,
    }

    return render(request, 'wishlist.html', context)

@login_required
def remove_from_wishlist(request, product_id):

    Wishlist.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()

    return redirect('wishlist_view')


@login_required(login_url="/login")
def checkout(request):

    cart = Cart.objects.filter(user=request.user)

    if not cart.exists():
        return redirect("cart_view")

    total_amount = sum(item.total_price for item in cart)

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        request.session["checkout_data"] = {
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
        }

        line_items = []

        for item in cart:
            line_items.append({
                "price_data": {
                    "currency": "inr",
                    "product_data": {
                        "name": item.product.name,
                    },
                    "unit_amount": int(item.product.price * 100),
                },
                "quantity": item.quantity,
            })

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=line_items,
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            customer_email=email,
        )

        return redirect(checkout_session.url, code=303)

    return render(
        request,
        "checkout.html",
        {
            "cart": cart,
            "total_amount": total_amount,
        },
    )


@login_required(login_url="/login")
def payment_success(request):

    cart = Cart.objects.filter(user=request.user)

    if not cart.exists():
        return redirect("cart_view")

    checkout = request.session.get("checkout_data")

    total_amount = sum(item.total_price for item in cart)

    order = Order.objects.create(
        user=request.user,
        name=checkout["name"],
        email=checkout["email"],
        phone=checkout["phone"],
        address=checkout["address"],
        total_amount=total_amount,
        status="Paid",
    )

    for item in cart:

        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )

    cart.delete()

    if "checkout_data" in request.session:
        del request.session["checkout_data"]

    return render(request, "payment_success.html", {
        "order": order
    })

@login_required(login_url="/login")
def payment_cancel(request):

    return render(request, "payment_cancel.html")
