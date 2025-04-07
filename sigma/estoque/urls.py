from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'estoque'

urlpatterns = [
    # URLs públicas
    path('', views.inicio, name='inicio'),

    # URLs de autenticação
    path('accounts/login/', auth_views.LoginView.as_view(template_name='estoque/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # URLs protegidas (requerem login)
    path('estoque/adicionar/', views.adicionar_produto, name='adicionar_produto'),
    path('estoque/editar/<int:id>/', views.editar_produto, name='editar_produto'),
    path('estoque/remover/<int:id>/', views.remover_produto, name='remover_produto'),
    path('recomendacoes/', views.lista_recomendacoes, name='lista_recomendacoes'),
    path('compras/', views.aprovar_compras, name='aprovar_compras'),
    path('compras/exportar/', views.exportar_pdf, name='exportar_pdf'),
    path('estoque/', views.lista_produtos, name='lista_produtos'),
    path('dashboard/', views.dashboard, name='dashboard'),
]