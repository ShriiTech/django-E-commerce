from django.contrib import admin
from .models import Order,OrdersItem,Coupon


class OrderItemInline(admin.TabularInline):
    model = OrdersItem
    raw_id_fields = ('product', )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'user', 'updated', 'paid')
    list_filter = ('paid', )
    inlines = (OrderItemInline, )


admin.site.register(Coupon)
