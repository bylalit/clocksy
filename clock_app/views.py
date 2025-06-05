from django.shortcuts import get_object_or_404, render, redirect
from .models import Category, Product, Brand
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

def index(request):
    # data = request.GET.get('search')
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.all()[:8]
    return render(request, 'index.html', {'categories': categories, 'products': products, 'brands': brands})

def category(request, name):
    categories = Category.objects.all()
    # print(categories)
    category = Category.objects.get(name=name)
    # print(category)
    
    sort_order = request.GET.get('sort')
    if sort_order == "low":
        products = category.product_set.all().order_by('price')
        print(products)
    elif sort_order == "high":
        products = category.product_set.all().order_by('-price')
        print(products)
    else:
        products = category.product_set.all()
        
    brand = Brand.objects.all()
    return render(request, 'category.html', {'categories': categories,'products': products, 'brands': brand,'name': name})

def singal_product(request, product_id):
    categories = Category.objects.all()
    product = Product.objects.get(id=product_id)
    brands = Brand.objects.all()
    # releted product
    related_product = Product.objects.filter(category=product.category)[:8]
    return render(request, 'singal_product.html', {'categories': categories, 'products': product, 'related_products': related_product, 'brands': brands})


@login_required(login_url='/login')
def add_to_cart(request, product_id):
    
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    if str(product.id) in cart:
        cart[str(product.id)]['quantity'] += 1
    else:
        cart[str(product.id)] = {
            "name" : product.name,
            "price" : product.price,
            "quantity" : 1,
            "image" : product.image1.url if product.image1 else None, 
        }
    
    request.session['cart'] = cart
    request.session.modified = True
    # print(cart)
    return redirect("cart_view")


def cart_view(request):
    cart = request.session.get("cart", {})
    total_amount = sum(item['price'] * item['quantity'] for item in cart.values())

    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'cart.html', {'cart': cart, 'categories': categories, 'brands': brands, 'total_amount': total_amount})


def update_cart(request, product_id, action):
    # print(product_id)
    # print(action)
    cart = request.session.get('cart', {})
    
    if(str(product_id)) in cart:
        if action == "increase":
            cart[str(product_id)]['quantity'] += 1
        elif action == "decrease":
            if cart[str(product_id)]['quantity'] > 1:
                cart[str(product_id)]['quantity'] -= 1
            else:
                del cart[str(product_id)]
                
    request.session['cart'] = cart
    request.session.modified = True
    return redirect("cart_view")


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        request.session.modified = True
        
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


def search_page(req):
    data = req.POST.get('search')
    results = Product.objects.filter(name__icontains=data)
    print(results)
    categories = Category.objects.all()
    return render(req, 'search_page.html', {'categories': categories, 'results': results})


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


def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishcart = request.session.get('wishcart', {})
    
    wishcart[str(product_id)] = {
        'name': product.name,
        'price': product.price,
        'image': product.image1.url if product.image1 else None,
    }
    
    request.session['wishcart'] = wishcart
    request.session.modified = True
    return redirect('wishlist_view')


def wishlist_view(request):
    wishcart = request.session.get('wishcart')
    # print(wishcart)
    categories = Category.objects.all()
    brand = Brand.objects.all()
    return render(request, 'wishlist.html', {'wishcart': wishcart, 'categories': categories, 'brands':brand})


def remove_from_wishlist(request, product_id):
    wishcart = request.session.get("wishcart", {})
    
    if str(product_id) in wishcart:
        del wishcart[str(product_id)]
        request.session['wishcart'] = wishcart
        request.session.modified = True
        
    return redirect("wishlist_view")




# views.py

import razorpay
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # optional for POST testing



def payment_page(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    payment = client.order.create({
        "amount": 50000,  # 500.00 INR in paise
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "payment": payment,
        "key": settings.RAZORPAY_KEY_ID
    }
    return render(request, "payment_sir.html", context)



def payment(request):
    cart = request.session.get("cart", {})
    total_amount = sum(item['price'] * item['quantity'] for item in cart.values())
    
    total_amount = sum(item['price'] * item['quantity'] for item in cart.values())
        
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    price = int(total_amount*100)
    
    data = {
        "amount": price,  # Amount in paise (₹500)
        "currency": "INR",
        "payment_capture": 1  # Auto capture
    }
    order = client.order.create(data)

    return render(request, "payment.html", {"order_id": order["id"], "razorpay_key": settings.RAZORPAY_KEY_ID})
    
    
    
    
    
    # client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
      
    # payment = client.order.create({
    #     "amount": int(total_amount * 100),  # 500.00 INR in paise
    #     "currency": "INR",
    #     "payment_capture": "1"
    # })    
    
   
    # context = {
    #     'payment': payment,
    #     'key': settings.RAZORPAY_KEY_ID,
    #     'cart': cart,
    #     'total_amount': total_amount,
    # }

    # return render(request, 'payment.html', context)


