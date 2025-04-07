from django.db import models

class Produto(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    quantidade = models.IntegerField(default=0)
    localizacao = models.CharField(max_length=100, blank=True, verbose_name="Localização")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    parado_mais_um_ano = models.BooleanField(default=False, verbose_name="Parado há mais de 1 ano")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"