from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    FILIAIS_CHOICES = [
        ('SP', 'São Paulo'),
        ('RJ', 'Rio de Janeiro'),
    ]
    filial = models.CharField(max_length=2, choices=FILIAIS_CHOICES, default='SP')

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.username} ({self.get_filial_display()})"

class Produto(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    quantidade = models.IntegerField(default=0)
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Preço Unitário"
    )
    localizacao = models.CharField(max_length=100, blank=True, verbose_name="Localização")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    parado_mais_um_ano = models.BooleanField(default=False, verbose_name="Parado há mais de 1 ano")
    filial = models.CharField(max_length=2, choices=CustomUser.FILIAIS_CHOICES, default='SP')

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']

    def __str__(self):
        return f"{self.codigo} - {self.nome} ({self.get_filial_display()})"
    
class HistoricoMovimentacao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    data = models.DateField()
    tipo = models.CharField(max_length=10, choices=[('ENTRADA', 'Entrada'), ('SAIDA', 'Saída')])
    quantidade = models.IntegerField()
    origem = models.CharField(max_length=100, blank=True)  # Ex: "Compra", "Ajuste"
    registrado_por = models.ForeignKey(
        'CustomUser',  # Alterado para referenciar diretamente o CustomUser
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Registrado por"
    )

    class Meta:
        verbose_name = "Histórico de Movimentação"
        verbose_name_plural = "Históricos de Movimentação"
        ordering = ['-data']

    def __str__(self):
        return f"{self.produto.nome} - {self.tipo} {self.quantidade}"

class RecomendacaoCompra(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADA', 'Aprovada'),
        ('REJEITADA', 'Rejeitada')
    ]
    
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade_recomendada = models.IntegerField()
    motivo = models.CharField(max_length=20, choices=[
        ('ESTOQUE_BAIXO', 'Estoque Baixo'),
        ('HISTORICO', 'Histórico de Consumo')
    ])
    data_criacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    criado_por = models.ForeignKey(
        'CustomUser',  # Alterado para referenciar diretamente o CustomUser
        on_delete=models.CASCADE,
        verbose_name="Criado por"
    )

    class Meta:
        verbose_name = "Recomendação de Compra"
        verbose_name_plural = "Recomendações de Compra"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"{self.produto.nome} - {self.quantidade_recomendada} ({self.get_status_display()})"