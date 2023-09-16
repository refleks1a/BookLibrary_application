from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import *

urlpatterns = [
    path('', Library.as_view(), name='library'),

    path('book/<int:pk>', BookDetail.as_view(), name='book'),

    path('log_in/', CustomLogInView.as_view(), name='log_in'),
    path('log_out/', LogoutView.as_view(next_page='library'), name='log_out'),
    path('sign_up/', CustomSignUpView.as_view(), name='sign_up'),

    path('cart/', MyBooks.as_view(), name='cart'),
    path('update_item/', UpdateItem, name='update_item')
]
