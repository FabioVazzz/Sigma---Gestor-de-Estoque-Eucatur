from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from django.http import HttpResponse

def gerar_pdf_recomendacoes(recomendacoes):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Cabeçalho
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Recomendações de Compra")
    
    # Conteúdo
    y = 700
    p.setFont("Helvetica", 12)
    for rec in recomendacoes:
        p.setFillColor(colors.blue if rec.motivo == 'HISTORICO' else colors.red)
        p.drawString(100, y, f"{rec.produto.nome} - {rec.quantidade_recomendada} unidades")
        y -= 20
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer