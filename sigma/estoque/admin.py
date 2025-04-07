from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Produto, HistoricoMovimentacao, RecomendacaoCompra

# Configuração personalizada para o CustomUser
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'filial', 'is_staff')
    list_filter = ('filial', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
        ('Informações da Filial', {'fields': ('filial',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'filial', 'is_staff', 'is_active'),
        }),
    )

# Configuração para Produto
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'quantidade', 'filial', 'localizacao', 'parado_mais_um_ano')
    list_filter = ('filial', 'parado_mais_um_ano')
    search_fields = ('codigo', 'nome', 'descricao')
    readonly_fields = ('data_cadastro', 'ultima_atualizacao')
    list_per_page = 20

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(filial=request.user.filial)

# Configuração para HistoricoMovimentacao
class HistoricoMovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'data', 'tipo', 'quantidade', 'origem', 'registrado_por')
    list_filter = ('tipo', 'data', 'produto__filial')
    search_fields = ('produto__nome', 'origem')
    date_hierarchy = 'data'
    raw_id_fields = ('produto',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(produto__filial=request.user.filial)

# Configuração para RecomendacaoCompra
class RecomendacaoCompraAdmin(admin.ModelAdmin):
    list_display = ('produto', 'quantidade_recomendada', 'status', 'motivo', 'criado_por', 'data_criacao')
    list_filter = ('status', 'motivo', 'produto__filial')
    search_fields = ('produto__nome',)
    actions = ['aprovar_recomendacoes']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(produto__filial=request.user.filium)
    
    def aprovar_recomendacoes(self, request, queryset):
        queryset.update(status='APROVADA')
    aprovar_recomendacoes.short_description = "Aprovar recomendações selecionadas"

# Registro único dos modelos
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Produto, ProdutoAdmin)
admin.site.register(HistoricoMovimentacao, HistoricoMovimentacaoAdmin)
admin.site.register(RecomendacaoCompra, RecomendacaoCompraAdmin)