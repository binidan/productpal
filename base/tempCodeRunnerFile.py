def recommendation(request):
    products = {}  # Use a list to store multiple products
    if request.user.is_authenticated:
        user = request.user
        products_lst = Product.objects.filter(customer=user)
        for product in products_lst:
            title = product.title
            product_info = scrapper.product_scraper(title)
            print(f"Title: {title}, Product Info: {product_info}")

            if product_info:
                # Add the first product's key-value pairs to the 'products' dictionary
                for key, value in product_info.items():
                    print(f"Key: {key}, Value: {value}")
                break

    context = {
        'products_recom': products  # Pass the list of (key, value) pairs to the template
    }

    return render(request, 'base/shop.html', context)