import logging

from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .cart import SessionCart
from home.models import Product
from .forms import CartAddForm, CouponApplyForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order, OrdersItem, Coupon
from django.contrib import messages


logger = logging.getLogger(__name__)  # 🔥 لاگر اصلی


class CartView(View):
    def get(self, request):
        cart = SessionCart(request)
        return render(request, 'orders/cart.html', {'cart': cart})


class CartAddView(View):
    def post(self, request, product_id):
        cart = SessionCart(request)
        product = get_object_or_404(Product, id=product_id)
        form = CartAddForm(request.POST)
        if form.is_valid():
            cart.add(product, form.cleaned_data['quantity'])
        return redirect('orders:cart')


class CartRemoveView(View):
    def get(self, request, product_id):
        cart = SessionCart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect('orders:cart')


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        form = CouponApplyForm()
        return render(request, 'orders/order.html', {'order': order, 'form': form})


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        cart = SessionCart(request)
        order = Order.objects.create(user=request.user)
        for item in cart:
            OrdersItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )
        cart.clear()
        return redirect('orders:order_detail', order.id)


class CouponApplyView(LoginRequiredMixin, View):
    form_class = CouponApplyForm

    def post(self, request, order_id):
        logger.info("CouponApplyView POST called")
        logger.info(f"Order ID: {order_id}")
        logger.info(f"POST data: {request.POST}")

        try:
            now = timezone.now()
            logger.info(f"Current time: {now}")

            order = get_object_or_404(Order, id=order_id)
            logger.info(f"Order found: {order.id}")

            form = self.form_class(request.POST)

            if not form.is_valid():
                logger.warning(f"Form invalid: {form.errors}")
                messages.error(request, "Invalid form")
                return redirect('orders:order_detail', order_id)

            code = form.cleaned_data['code']
            logger.info(f"Coupon code entered: {code}")

            try:
                coupon = Coupon.objects.get(
                    code__exact=code,
                    valid_from__lte=now,
                    valid_to__gte=now,
                    active=True
                )
                logger.info(
                    f"Coupon found: {coupon.code} | discount={coupon.discount}"
                )

                order.discount = coupon.discount
                order.save()
                logger.info("Order updated with discount")

                messages.success(request, 'Coupon applied successfully!')

            except Coupon.DoesNotExist:
                logger.warning(f"Coupon NOT found or expired: {code}")
                messages.error(
                    request, 'This coupon does not exist or has expired.'
                )

        except Exception as e:
            logger.exception("🔥 Unexpected error in CouponApplyView")
            messages.error(request, "Internal server error")

        return redirect('orders:order_detail', order_id)