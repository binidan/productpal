from django.shortcuts import render, redirect
from .forms import MyUserCreationForm, UserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Customer, Product
from . import scrapper
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product  # Import your Product model here

@csrf_exempt  # This decorator allows the view to accept POST requests without CSRF tokens for simplicity.
def add_to_wishlist(request):
    if request.method == 'POST' and request.user.is_authenticated:
        # Retrieve product data from the JSON request body
        data = json.loads(request.body)
        link = data.get('link')
        img = data.get('img')
        title = data.get('title')
        price = data.get('price')
        rate_star = data.get('rate_star')
        rate_empty = data.get('rate_empty')
        company = data.get('company')

        # Create a new Product instance and save it to the database
        product = Product(
            customer=request.user,
            title=title,
            company=company,
            rate=rate_star,
            price=price,
            discount='',  # You may need to handle discounts separately
            link=link,
            img_src=img,
        )
        product.save()

        return JsonResponse({'message': 'Product added to wishlist'})

    return JsonResponse({'message': 'Error adding product to wishlist'}, status=400)


def wishlist(request):
    if request.user.is_authenticated:
        customer = request.user
        try:
            products = Product.objects.filter(customer=customer)

        except Product.DoesNotExist:
            pass

    context = {
        'products':products,
    }
    return render(request, 'base/wishlist.html', context)


def shop(request):
    q = request.GET.get('q', '')  # Get the search query from the URL
    sort_option = request.GET.get('sort_option', '')  # Get the sorting option from the URL

    products = scrapper.product_scraper(q)

    # Handle sorting based on the sort_option
    if sort_option == "Amazon":
        new_dict = products.copy()
        products = {}
        for key, value in new_dict.items():
            if value.get("company") == "amazon":
                products[key] = value
    if sort_option == "Snappdeal":
        new_dict = products.copy()
        products = {}
        for key, value in new_dict.items():
            if value.get("company") == "snapdeal":
                products[key] = value
    if sort_option == "Name (A - Z)":
        products = dict(sorted(products.items(), key=lambda item: item[0]))
    elif sort_option == "Name (Z - A)":
        products = dict(sorted(products.items(), key=lambda item: item[0], reverse=True))
    elif sort_option == "Price (Low - High)":
        products = dict(sorted(products.items(), key=lambda item: int(item[1]['price'][1:].replace(',', '')) if item[1]['price'] is not None else 0))
    elif sort_option == "Price (High - Low)":
        products = dict(sorted(products.items(), key=lambda item: int(item[1]['price'][1:].replace(',', '')) if item[1]['price'] is not None else 0, reverse=True))
    elif sort_option == "Rate (High - Low)":
        products = dict(sorted(products.items(), key=lambda item: float(item[1]['rate']) if item[1]['rate'] is not None else -float('inf'), reverse=True))
    elif sort_option == "Rate (Low - High)":
        products = dict(sorted(products.items(), key=lambda item: float(item[1]['rate']) if item[1]['rate'] is not None else 0.0))
    
    for title, data in products.items():
        if data['rate'] is not None:
            data['rating_stars'] = range(round(float(data['rate'])))
            data['empty_stars'] = range(5 - round(float(data['rate'])))
    products_recom = {}  # Use a list to store multiple products
    if request.user.is_authenticated:
        customer = request.user
        products_lst = Product.objects.filter(customer=customer)
        for product in products_lst:
            title = product.title
            product_info = scrapper.product_scraper(title)

            if product_info:
                # Add the first product's key-value pairs to the 'products' dictionary
                for key, value in product_info.items():
                    products_recom[key] = value
                    break

    context = {
        'products_recom': products_recom,
        'products': products,
        'q': q,  # Pass the search query back to the template
    }
    return render(request, 'base/shop.html', context)


def loginPage(request):
    page = 'login'
    login_form = UserForm()

    if request.user.is_authenticated:
        return redirect('shop')

    if request.method == 'POST':
        messages.success(request, None)
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = Customer.objects.get(username=username)
        except Customer.DoesNotExist:  # Catch the specific exception
            messages.error(request, 'User does not exist')
            return redirect('login')  # Redirect back to the login page

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('shop')
        else:
            messages.error(request, "Username and password do not match")

    context = {'page': page, 'login_form': login_form}
    return render(request, 'base/login-register.html', context)

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('shop')
    
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('shop')
        else:
            messages.error(request, 'An error occured during registration')
    return render(request, "base/login-register.html", {'form':form})

def logoutUser(request):
    logout(request)
    return redirect('shop')

