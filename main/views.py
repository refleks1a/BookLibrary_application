import json

from django.db.models import Q

from PIL import Image
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.db.models import QuerySet
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, path

from django.views.generic import ListView, DetailView, FormView

from .models import *


class CustomLogInView(LoginView):
    template_name = 'main/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['categories'] = Category.objects.all()
        return context

    def get_success_url(self):
        return reverse_lazy('library')


class CustomSignUpView(FormView):
    template_name = 'main/sign_up.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('library')

    def form_valid(self, form):
        user = form.save()
        if user:
            login(self.request, user)
        return super(CustomSignUpView, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('library')
        return super(CustomSignUpView, self).get(*args, **kwargs)


class Library(ListView):
    model = Book
    template_name = 'main/library.html'
    context_object_name = 'books'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        category = self.request.GET.get('category')

        search_input = self.request.GET.get('search-area') or ''

        if category is None:
            context['books'] = context['books'].all()
        else:
            context['books'] = context['books'].filter(category__name=category)

        if search_input:
            context['books'] = context['books'].filter(Q(title__icontains=search_input) | Q(author__icontains=search_input))

        context['books'] = context['books'][:8]
        context['categories'] = Category.objects.all()
        context['category'] = category
        context['bg-image'] = Image.open('static/images/background_image.webp')
        context['search_input'] = search_input
        return context


class MyBooks(ListView):
    model = Book
    template_name = 'main/my_books.html'
    context_object_name = 'books'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user
        book = self.request.GET.get('book')
        customer = self.request.user
        order, created = Order.objects.get_or_create(customer=customer)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

        context['order'] = order
        context['items'] = items
        context['cartItems'] = cartItems
        context['categories'] = Category.objects.all()
        return context


class BookDetail(DetailView):
    model = Book
    template_name = 'main/book.html'
    context_object_name = 'book'


def UpdateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action', action)
    print('Product ID', productId)

    customer = request.user
    product = Book.objects.get(id=productId)
    order, create = Order.objects.get_or_create(customer=customer)

    orderItem, create = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


