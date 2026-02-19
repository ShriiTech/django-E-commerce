from django.contrib import admin
from home.models import Category, Product

admin.site.register(Category)

@admin.register(Product)
class ProductAdmin (admin.ModelAdmin):
    filter_horizontal = ('category',) 