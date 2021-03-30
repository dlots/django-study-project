from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.template import loader

from .models import Product
from .forms import AddToCartForm, LoginForm, RegistrationForm, CheckoutForm


SESSION_CHECKOUT_ID = 'checkout_in_progress'
SESSION_CART_ID = 'cart'

def log_out(request):
    checkout_in_progress = bool(request.session.get(SESSION_CHECKOUT_ID))
    if checkout_in_progress:
        cart = request.session.get(SESSION_CART_ID)
        if cart:
            ids = list(cart)
            products = Product.objects.filter(id__in=ids)
            for product in products:
                id = str(product.id)
                product.in_stock += cart[id]
    logout(request)
    redirect_url = request.GET.get('next') or reverse('shop_catalog')
    return redirect(redirect_url)


def log_in(request):
    if request.method == 'POST':
        logout(request)
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(request.GET['next'])
            else:
                form.add_error('Invalid credentials!')
    else:  # GET
        form = LoginForm()
    return render(request, 'shop/login.html', {'form': form})


def sign_up(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            logout(request)
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            password_again = form.cleaned_data['password_again']
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'User already exists!')
            elif password != password_again:
                form.add_error('password_again', 'Password mismatch!')
            else:
                user = User.objects.create_user(username, email, password)
                login(request, user)
                return render(request, 'shop/cart.html', {})
    else:  # GET
        form = RegistrationForm()
    return render(request, 'shop/signup.html', {'form': form})


def render_catalog(request):
    products = Product.objects.all().order_by('name')
    context = {'products': products}
    return render(request, 'shop/catalog.html', context)


def product(request, product_id):
    if request.method == 'POST':
        return add_to_cart(request, product_id)
    else:
        return render_product(request, product_id)


def render_product(request, product_id, additional_context={}):
    product = get_object_or_404(Product, id=product_id)
    if 'form' in additional_context:
        form = additional_context['form']
    else:
        form = AddToCartForm()
    context = {
        'product': product,
        'form': form,
    }
    return render(request, 'shop/product.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = AddToCartForm(request.POST)
    context = {}
    if form.is_valid():
        product_id = str(product_id)
        quantity = form.cleaned_data['quantity']
        cart = request.session.get(SESSION_CART_ID)
        if not cart:
            cart = {}
        if product_id in cart:
            if cart[product_id] + quantity > product.in_stock:
                form.add_error('quantity', 'You have %s of %s in cart and trying to add %s more, but we have only %s!' % (cart[product_id], product.name, quantity, product.in_stock))
                context['form'] = form
                return render_product(request, product_id, context)
            else:
                cart[product_id] += quantity
                request.session[SESSION_CART_ID] = cart
        else:
            if quantity > product.in_stock:
                form.add_error('quantity', 'You are trying to add %s of %s, but we have only %s!' % (quantity, product.name, product.in_stock))
                context['form'] = form
                return render_product(request, product_id, context)
            else:
                cart[product_id] = quantity
                request.session[SESSION_CART_ID] = cart
    return HttpResponseRedirect(reverse('product_by_id', kwargs={'product_id': product_id}))


def request_cart(request):
    if request.method == 'POST':
        return prepare_checkout(request)
    else:
        return render_cart(request)


def render_cart(request, additional_context={}):
    cart = request.session.get(SESSION_CART_ID)
    product_ids = []
    empty = True
    if cart:
        product_ids = list(cart)
        empty = False
    products = Product.objects.filter(id__in=product_ids).order_by('name')
    total_cost = 0
    positions = []
    for product in products:
        id = str(product.id)
        positions.append((product, cart[id], product.price * cart[id]))
        total_cost += positions[-1][2]
    context = {
        'empty': empty,
        'positions': positions,
        'total_cost': total_cost,
        **additional_context,
    }
    return render(request, 'shop/cart.html', context)


def prepare_checkout(request):
    cart = request.session.get(SESSION_CART_ID)
    product_ids = list(cart)
    products = Product.objects.filter(id__in=product_ids).order_by('name')
    checkout_in_progress = bool(request.session.get(SESSION_CHECKOUT_ID))
    if not checkout_in_progress:
        errors = []
        for product in products:
            id = str(product.id)
            if product.in_stock < cart[id]:
                errors.append('You are trying to order %s of %s, but we have only %s! Please change the quantity.' % (cart[id], product.name, product.in_stock))
        if len(errors) > 0:
            return render_cart(request, {'errors': errors})
        for product in products:
            id = str(product.id)
            product.in_stock -= cart[id]
            product.save(update_fields=['in_stock'])
        request.session[SESSION_CHECKOUT_ID] = True
    return redirect(reverse(checkout))


@login_required(login_url='/shop/shop_login/')
def checkout(request):
    if request.method == 'POST':
        return confirm_order(request)
    else:
        return render_checkout(request)


def render_checkout(request):
    form = CheckoutForm()
    cart = request.session.get(SESSION_CART_ID)
    product_ids = list(cart)
    products = Product.objects.filter(id__in=product_ids).order_by('name')
    total_cost = 0
    positions = []
    for product in products:
        id = str(product.id)
        positions.append((product, cart[id], product.price * cart[id]))
        total_cost += positions[-1][2]
    context = {
        'positions': positions,
        'total_cost': total_cost,
        'form': form,
    }
    return render(request, 'shop/checkout.html', context)


def confirm_order(request):
    print('confirm order')
