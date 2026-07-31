from django.shortcuts import get_object_or_404, render, redirect
from .models import Category, Product, Brand, Wishlist, Cart, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.contrib import messages
import stripe
from django.conf import settings
import cloudinary.uploader
stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.

def index(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.all()[:8]
    # print(products)
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

@login_required(login_url="/login")
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

@login_required(login_url="/login")
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
        
    categories = Category.objects.all()
    brand = Brand.objects.all()

    return render(request, "payment_success.html", {
        "order": order,
        "categories": categories,
        "brand": brand
    })

@login_required(login_url="/login")
def payment_cancel(request):

    return render(request, "payment_cancel.html")








# Admin View

def admin_login(request):
    # Agar admin pehle se logged in hai, to direct dashboard par bhej do
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:  # Check ki user Staff / Admin hai ya nahi
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Access Denied: You do not have admin permissions.')
        else:
            messages.error(request, 'Invalid admin username or password.')

    return render(request, 'admin_panel/admin_login.html')


def logout_admin(request):
    logout(request)
    return redirect(admin_login)

@staff_member_required(login_url='/custom-admin/login/')
def admin_dashboard(request):
    total_orders = Order.objects.count()

    total_products = Product.objects.count()

    revenue_data = Order.objects.exclude(status='Cancelled').aggregate(Sum('total_amount'))
    total_revenue = revenue_data['total_amount__sum'] or 0

    total_customers = User.objects.filter(is_staff=False).count()
    recent_orders = Order.objects.all().order_by('-id')[:10]

    context = {
        'total_orders': total_orders,
        'total_products': total_products,
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ================= CATEGORY CRUD =================

@staff_member_required(login_url='/custom-admin/login/')
def category_list(request):
    categories = Category.objects.all().order_by('-id')
    return render(request, 'admin_panel/category_list.html', {'categories': categories})

@staff_member_required(login_url='login')
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')

        if Category.objects.filter(name=name).exists():
            messages.error(request, 'Category with this name already exists!')
        else:
            Category.objects.create(name=name, image=image)
            messages.success(request, 'Category added successfully!')
            return redirect('category_list')

    return render(request, 'admin_panel/category_form.html', {'title': 'Add Category'})

@staff_member_required(login_url='/custom-admin/login/')
def update_category(request, id):
    category = get_object_or_404(Category, id=id)

    if request.method == 'POST':
        category.name = request.POST.get('name')

        new_image = request.FILES.get('image')

        if new_image:
            # Delete old image from Cloudinary
            if category.image:
                category.image.delete(save=False)

            category.image = new_image

        category.save()

        messages.success(request, 'Category updated successfully!')
        return redirect('category_list')

    return render(request, 'admin_panel/category_form.html', {
        'category': category,
        'title': 'Edit Category'
    })
    
    
@staff_member_required(login_url='/custom-admin/login/')
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)

    if category.image:
        try:
            category.image.delete(save=False)
        except Exception as e:
            print(e)

    category.delete()

    messages.success(request, 'Category deleted successfully!')
    return redirect('category_list')


# ================= BRAND CRUD =================

@staff_member_required(login_url='/custom-admin/login/')
def brand_list(request):
    brands = Brand.objects.all().order_by('-id')
    return render(request, 'admin_panel/brand_list.html', {'brands': brands})

@staff_member_required(login_url='/custom-admin/login/')
def add_brand(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')

        if Brand.objects.filter(name=name).exists():
            messages.error(request, 'Brand with this name already exists!')
        else:
            Brand.objects.create(name=name, image=image)
            messages.success(request, 'Brand added successfully!')
            return redirect('brand_list')

    return render(request, 'admin_panel/brand_form.html', {'title': 'Add Brand'})

@staff_member_required(login_url='/custom-admin/login/')
def update_brand(request, id):
    brand = get_object_or_404(Brand, id=id)

    if request.method == 'POST':
        brand.name = request.POST.get('name')

        new_image = request.FILES.get('image')

        if new_image:
            # Delete old image from Cloudinary
            if brand.image:
                brand.image.delete(save=False)

            brand.image = new_image

        brand.save()

        messages.success(request, 'Brand updated successfully!')
        return redirect('brand_list')

    return render(request, 'admin_panel/brand_form.html', {
        'brand': brand,
        'title': 'Edit Brand'
    })
    
    
@staff_member_required(login_url='/custom-admin/login/')
def delete_brand(request, id):
    brand = get_object_or_404(Brand, id=id)

    if brand.image:
        try:
            brand.image.delete(save=False)
        except Exception as e:
            print(e)

    brand.delete()

    messages.success(request, 'Brand deleted successfully!')
    return redirect('brand_list')


# ================= PRODUCT CRUD =================

@staff_member_required(login_url='/custom-admin/login/')
def admin_product_list(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'admin_panel/product_list.html', {'products': products})

@staff_member_required(login_url='/custom-admin/login/')
def admin_product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'admin_panel/product_detail.html', {'product': product})

@staff_member_required(login_url='/custom-admin/login/')
def add_product(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        price = request.POST.get('price')
        description = request.POST.get('description')
        
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')

        category = Category.objects.get(id=category_id) if category_id else None
        brand = Brand.objects.get(id=brand_id) if brand_id else None

        Product.objects.create(
            name=name,
            category=category,
            brand=brand,
            price=price,
            description=description,
            image1=image1,
            image2=image2,
            image3=image3
        )
        messages.success(request, 'Product created successfully!')
        return redirect('admin_product_list')

    context = {
        'title': 'Add New Product',
        'categories': categories,
        'brands': brands
    }
    return render(request, 'admin_panel/product_form.html', context)

@staff_member_required(login_url='/custom-admin/login/')
def update_product(request, id):
    product = get_object_or_404(Product, id=id)

    categories = Category.objects.all()
    brands = Brand.objects.all()

    if request.method == 'POST':

        product.name = request.POST.get('name')

        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')

        if category_id:
            product.category = Category.objects.get(id=category_id)

        if brand_id:
            product.brand = Brand.objects.get(id=brand_id)

        product.price = request.POST.get('price')
        product.description = request.POST.get('description')

        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')

        if image1:
            if product.image1:
                product.image1.delete(save=False)
            product.image1 = image1

        if image2:
            if product.image2:
                product.image2.delete(save=False)
            product.image2 = image2

        if image3:
            if product.image3:
                product.image3.delete(save=False)
            product.image3 = image3

        product.save()

        messages.success(request, 'Product updated successfully!')
        return redirect('admin_product_list')

    context = {
        'title': 'Edit Product',
        'product': product,
        'categories': categories,
        'brands': brands,
    }

    return render(request, 'admin_panel/product_form.html', context)

@staff_member_required(login_url='/custom-admin/login/')
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    # Delete images from Cloudinary
    for image in [product.image1, product.image2, product.image3]:
        if image:
            try:
                image.delete(save=False)
            except Exception as e:
                print(e)

    product.delete()

    messages.success(request, 'Product deleted successfully!')
    return redirect('admin_product_list')


# ================= ORDER MANAGEMENT =================

@staff_member_required(login_url='/custom-admin/login/')
def admin_order_list(request):
    status_filter = request.GET.get('status')
    
    if status_filter:
        orders = Order.objects.filter(status=status_filter).order_by('-id')
    else:
        orders = Order.objects.all().order_by('-id')

    context = {
        'orders': orders,
        'current_status': status_filter
    }
    return render(request, 'admin_panel/order_list.html', context)


@staff_member_required(login_url='/custom-admin/login/')
def admin_order_detail(request, id):
    order = get_object_or_404(Order, id=id)
    
    # If OrderItem model exists, fetch items related to this order
    order_items = OrderItem.objects.filter(order=order) if 'OrderItem' in globals() else []

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {new_status}!')
            return redirect('admin_order_detail', id=order.id)

    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, 'admin_panel/order_detail.html', context)

