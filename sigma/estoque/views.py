from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum, F
from datetime import datetime, timedelta
from .models import Produto, HistoricoMovimentacao, RecomendacaoCompra
from .forms import ProdutoForm
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from .pdf import gerar_pdf_recomendacoes

# Helpers para verificação de grupos
def is_suprimentos(user):
    return user.groups.filter(name='Suprimentos').exists()

def is_compras(user):
    return user.groups.filter(name='Compras').exists()

# Views existentes (mantidas intactas)
def inicio(request):
    """View para a página inicial do sistema"""
    return render(request, 'estoque/inicio.html')

from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ProdutoForm

@login_required
def adicionar_produto(request):
    """View para adicionar um novo produto com controle de filial"""
    template_name = 'estoque/adicionar_produto.html'
    context = {
        'filial_usuario': request.user.get_filial_display(),
        'titulo_pagina': 'Adicionar Novo Produto'
    }

    if request.method == 'POST':
        form = ProdutoForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                produto = form.save()
                messages.success(
                    request,
                    f'✅ Produto "{produto.nome}" adicionado com sucesso! '
                    f'(Filial: {produto.get_filial_display()}, Código: {produto.codigo})'
                )
                return redirect('estoque:lista_produtos')
            except Exception as e:
                messages.error(
                    request,
                    f'❌ Erro ao salvar produto: {str(e)}'
                )
        else:
            messages.error(
                request,
                '❌ Por favor, corrija os erros abaixo'
            )
    else:
        form = ProdutoForm(user=request.user)
    
    context['form'] = form
    return render(request, template_name, context)

def editar_produto(request, id):
    """View para editar um produto existente"""
    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('estoque:lista_produtos')
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'estoque/adicionar_produto.html', {'form': form})

def remover_produto(request, id):
    """View para remover um produto"""
    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        produto.delete()
        return redirect('estoque:lista_produtos')
    return render(request, 'estoque/confirmar_remocao.html', {'produto': produto})

@login_required
@login_required
def lista_produtos(request):
    """View para listar produtos com busca - FILTRADO POR FILIAL"""
    search_term = request.GET.get('q', '')
    produtos = Produto.objects.filter(filial=request.user.filial)  # Filtro por filial
    
    if search_term:
        produtos = produtos.filter(
            Q(nome__icontains=search_term) | 
            Q(codigo__icontains=search_term) |
            Q(descricao__icontains=search_term)
        ).order_by('nome')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'estoque/partials/linhas_produtos.html', {'produtos': produtos})
    
    return render(request, 'estoque/lista_produtos.html', {
        'produtos': produtos,
        'filial_usuario': request.user.get_filial_display()  # Adicionado para mostrar no template
    })

@login_required
@login_required
def dashboard(request):
    """
    Dashboard de estoque - FILTRADO POR FILIAL
    """
    PRECO_PADRAO = 100.00  # Substitua por um campo real se necessário

    # Todos os filtros agora incluem filial do usuário
    valor_total = Produto.objects.filter(filial=request.user.filial).aggregate(
        total=Sum(F('quantidade') * PRECO_PADRAO)
    )['total'] or 0

    valor_inativo = Produto.objects.filter(
        filial=request.user.filial,
        parado_mais_um_ano=True
    ).aggregate(
        total=Sum(F('quantidade') * PRECO_PADRAO)
    )['total'] or 0

    qtd_ativos = Produto.objects.filter(filial=request.user.filial, parado_mais_um_ano=False).count()
    qtd_inativos = Produto.objects.filter(filial=request.user.filial, parado_mais_um_ano=True).count()

    context = {
        'valor_total': valor_total,
        'valor_inativo': valor_inativo,
        'qtd_ativos': qtd_ativos,
        'qtd_inativos': qtd_inativos,
        'filial_usuario': request.user.get_filial_display()  # Adicionado
    }
    return render(request, 'estoque/dashboard.html', context)

# --- NOVAS VIEWS PARA RECOMENDAÇÃO DE COMPRAS ---

@login_required
@login_required
def gerar_recomendacoes(request):
    """Gera recomendações apenas para produtos da filial do usuário"""
    if not request.user.has_perm('estoque.add_recomendacaocompra'):
        messages.error(request, 'Você não tem permissão para executar esta ação.')
        return redirect('estoque:inicio')

    # 1. Itens com estoque baixo (apenas da filial)
    produtos_estoque_baixo = Produto.objects.filter(
        filial=request.user.filial,
        quantidade__lt=5
    ).annotate(
        quantidade_recomendada=5 - F('quantidade')
    )

    # 2. Itens com alto histórico de saída (apenas da filial)
    tres_meses_atras = datetime.now() - timedelta(days=90)
    
    produtos_consumo = HistoricoMovimentacao.objects.filter(
        produto__filial=request.user.filial,  # Filtro por filial
        tipo='SAIDA',
        data__gte=tres_meses_atras
    ).values('produto').annotate(
        total_saidas=Sum('quantidade')
    ).order_by('-total_saidas')[:10]

    # ... resto do código permanece igual ...
@login_required
@user_passes_test(is_suprimentos)
@login_required
@user_passes_test(is_suprimentos)
def lista_recomendacoes(request):
    """Lista recomendações apenas da filial do usuário"""
    if request.method == 'POST':
        # Processar edições/aprovações
        for key, value in request.POST.items():
            if key.startswith('quantidade_'):
                rec_id = key.split('_')[1]
                recomendacao = get_object_or_404(RecomendacaoCompra, id=rec_id, produto__filial=request.user.filial)
                recomendacao.quantidade_recomendada = value
                recomendacao.save()
            
            elif key.startswith('aprovar_'):
                rec_id = key.split('_')[1]
                recomendacao = get_object_or_404(RecomendacaoCompra, id=rec_id, produto__filial=request.user.filial)
                recomendacao.status = 'APROVADA'
                recomendacao.save()
            
            elif key.startswith('rejeitar_'):
                rec_id = key.split('_')[1]
                recomendacao = get_object_or_404(RecomendacaoCompra, id=rec_id, produto__filial=request.user.filial)
                recomendacao.status = 'REJEITADA'
                recomendacao.save()

        messages.success(request, 'Alterações salvas com sucesso!')
        return redirect('estoque:lista_recomendacoes')

    recomendacoes = RecomendacaoCompra.objects.filter(
        produto__filial=request.user.filial,
        status='PENDENTE'
    )
    return render(request, 'estoque/lista_recomendacoes.html', {
        'recomendacoes': recomendacoes,
        'filial_usuario': request.user.get_filial_display()
    })

@login_required
@user_passes_test(is_compras)
@login_required
@user_passes_test(is_compras)
def aprovar_compras(request):
    """Aprova compras apenas da filial do usuário"""
    recomendacoes = RecomendacaoCompra.objects.filter(
        produto__filial=request.user.filial,
        status__in=['PENDENTE', 'APROVADA']
    )
    
    return render(request, 'estoque/aprovar_compras.html', {
        'recomendacoes': recomendacoes,
        'titulo': 'Recomendações de Compra',
        'filial_usuario': request.user.get_filial_display()
    })

def exportar_pdf(request):
    """Exporta PDF apenas com recomendações da filial"""
    recomendacoes = RecomendacaoCompra.objects.filter(
        produto__filial=request.user.filial,
        status='APROVADA'
    )
    pdf = gerar_pdf_recomendacoes(recomendacoes)
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recomendacoes_{request.user.filial}.pdf"'
    return response