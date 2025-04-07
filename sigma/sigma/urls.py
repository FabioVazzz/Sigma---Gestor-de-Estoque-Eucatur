from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # Importe as views de autenticação
from estoque import views  # Importe as views do seu app estoque

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rota raiz redireciona para o login
    path('', auth_views.LoginView.as_view(template_name='estoque/login.html'), name='login'),
    
    # Inclui as URLs do app estoque com namespace
    path('estoque/', include('estoque.urls', namespace='estoque')),
]