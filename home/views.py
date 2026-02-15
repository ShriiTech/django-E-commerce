from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from home.models import Product, Category
from orders.forms import CartAddForm

class HomePage(View):
    def get(self, request, category_slug=None):
        products = Product.objects.filter(available=True)
        categories = Category.objects.filter(is_sub=False)

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)

        form = CartAddForm()  # فرم برای افزودن به سبد
        return render(request, "home/home.html", {
            'products': products,
            'categories': categories,
            'form': form
        })


class ProductDetail(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        form = CartAddForm()
        return render(request, 'home/detail.html', {
            'product': product,
            'form': form
        })