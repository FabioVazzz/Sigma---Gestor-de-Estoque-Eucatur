from django import forms
from django.core.exceptions import ValidationError
from .models import Produto

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['codigo', 'nome', 'descricao', 'quantidade', 'preco_unitario', 'localizacao', 'parado_mais_um_ano']
        labels = {
            'codigo': 'Código',
            'descricao': 'Descrição',
            'preco_unitario': 'Preço Unitário (R$)',
            'localizacao': 'Localização no Armazém',
            'parado_mais_um_ano': 'Marcar como parado há mais de 1 ano',
        }
        widgets = {
            'descricao': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Descrição detalhada do produto'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único do produto'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do produto'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'preco_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'localizacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Corredor A, Prateleira 3'
            }),
            'parado_mais_um_ano': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'codigo': 'Código único de identificação do produto',
            'parado_mais_um_ano': 'Marque se o produto está parado no estoque há mais de 1 ano',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.fields['filial'] = forms.CharField(
                label='Filial',
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'readonly': 'readonly'
                }),
                initial=self.instance.get_filial_display(),
                help_text='Filial não pode ser alterada após criação'
            )

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo'].strip().upper()
        if Produto.objects.filter(codigo=codigo).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError("Este código já está em uso.")
        return codigo

    def clean(self):
        cleaned_data = super().clean()
        quantidade = cleaned_data.get('quantidade')
        parado = cleaned_data.get('parado_mais_um_ano')
        
        if quantidade == 0 and not parado:
            self.add_error('parado_mais_um_ano', 'Produtos com quantidade zero devem ser marcados como parados')
        
        return cleaned_data

    def save(self, commit=True):
        produto = super().save(commit=False)
        if not produto.pk and self.user:
            produto.filial = self.user.filial
        
        if commit:
            produto.save()
            self.save_m2m()
        return produto