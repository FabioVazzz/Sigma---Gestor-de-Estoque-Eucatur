from datetime import datetime, timedelta
from django.db.models import Sum, F
from .models import Produto, HistoricoMovimentacao

def gerar_recomendacoes():
    # 1. Itens com estoque baixo (ex: abaixo de 5 unidades)
    estoque_baixo = Produto.objects.filter(
        quantidade__lt=5
    ).annotate(
        quantidade_recomendada=5 - F('quantidade')
    ).values('id', 'quantidade_recomendada')

    # 2. Itens com alto histórico de saída (últimos 3 meses)
    tres_meses_atras = datetime.now() - timedelta(days=90)
    
    itens_consumo = HistoricoMovimentacao.objects.filter(
        tipo='SAIDA',
        data__gte=tres_meses_atras
    ).values('produto').annotate(
        total_saidas=Sum('quantidade')
    ).order_by('-total_saidas')[:10]  # Top 10 itens mais consumidos

    # 3. Criar recomendações
    recomendacoes = []
    
    for item in estoque_baixo:
        recomendacoes.append({
            'produto_id': item['id'],
            'quantidade': item['quantidade_recomendada'],
            'motivo': 'ESTOQUE_BAIXO'
        })
    
    for item in itens_consumo:
        recomendacoes.append({
            'produto_id': item['produto'],
            'quantidade': item['total_saidas'],
            'motivo': 'HISTORICO'
        })
    
    return recomendacoes