#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera planilha-q22-l8.xlsx a partir de dados/*.json.
Rodado automaticamente pelo GitHub Actions a cada alteração em dados/ (cotações
lançadas pelo site, avanço de etapas). NÃO editar a planilha à mão — ela é
sobrescrita a cada geração. A fonte de dados é o site/os JSONs.
"""
import json, datetime, pathlib
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DADOS = RAIZ / 'dados'
SAIDA = RAIZ / 'planilha-q22-l8.xlsx'

AZUL = '0E3A6B'; AZUL2 = '2E5E96'; CINZA = 'EEF4FB'; AMBAR = 'B8860B'; VERDE = '1E7A46'
RS = '"R$" #,##0'; RS2 = '"R$" #,##0.00'; PCT = '0.0%'

def J(nome):
    return json.loads((DADOS / nome).read_text(encoding='utf-8'))

etapas = J('etapas.json')['etapas']
itens = J('itens.json')['itens']
cots = J('cotacoes.json')['cotacoes']

wb = Workbook()
fina = Side(style='thin', color='C7D8EC')
BORDA = Border(bottom=fina)

def cabecalho(ws, linha, titulos, larguras):
    for i, (t, w) in enumerate(zip(titulos, larguras), start=1):
        c = ws.cell(row=linha, column=i, value=t)
        c.font = Font(name='Arial', size=9, bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor=AZUL)
        c.alignment = Alignment(vertical='center', wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[linha].height = 26
    ws.freeze_panes = ws.cell(row=linha + 1, column=1)

def corpo(ws, linha, valores, fmt=None, zebra=True):
    for i, v in enumerate(valores, start=1):
        c = ws.cell(row=linha, column=i, value=v)
        c.font = Font(name='Arial', size=9)
        c.border = BORDA
        c.alignment = Alignment(vertical='top', wrap_text=(i in (2, 3, 4, 11, 12)))
        if zebra and linha % 2 == 0:
            c.fill = PatternFill('solid', fgColor=CINZA)
        if fmt and i in fmt:
            c.number_format = fmt[i]

# ============================ 1 · RESUMO ============================
ws = wb.active; ws.title = 'Resumo'
ws['A1'] = 'RESIDÊNCIA Q22 · L8 — PLANILHA DE CUSTOS E MATERIAIS'
ws['A1'].font = Font(name='Arial', size=15, bold=True, color=AZUL)
ws['A2'] = 'Gerada automaticamente a partir dos dados do painel de obra · NÃO editar à mão'
ws['A2'].font = Font(name='Arial', size=9, italic=True, color='5A6B7D')
ws['A3'] = f"Gerada em {datetime.datetime.now(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=-3))).strftime('%d/%m/%Y %H:%M')} (BRT)"
ws['A3'].font = Font(name='Arial', size=8, color='5A6B7D')
for col, w in zip('ABCD', (34, 20, 20, 46)):
    ws.column_dimensions[col].width = w

n = len(etapas) + 1
linhas = [
    ('INDICADOR', 'VALOR', '', 'OBSERVAÇÃO'),
    ('Área construída', 183, 'm²', 'térreo 75 + garagem 27,5 + superior 62 + extensão 18'),
    ('Estimativa — faixa baixa', f'=SUM(Etapas!C3:C{n + 1})', '', 'soma das 13 etapas'),
    ('Estimativa — faixa alta', f'=SUM(Etapas!D3:D{n + 1})', '', 'soma das 13 etapas'),
    ('Custo/m² — baixo', '=B7/B6', '', 'referência CUB-SP R8-N: R$ 2.129,86'),
    ('Custo/m² — alto', '=B8/B6', '', 'diferença = sistemas premium (bomba de calor, automação, resinados)'),
    ('Total cotado/contratado', f'=SUM(Cotações!J2:J{max(len(cots) + 1, 2)})', '', 'soma de tudo lançado no site'),
    ('Custo real informado', f'=SUM(Etapas!I3:I{n + 1})', '', 'digitado na aba Etapas do site'),
    ('Cotações registradas', f'=COUNTA(Cotações!A2:A{max(len(cots) + 1, 2)})', '', 'cada lançamento = 1 commit no repositório'),
    ('Avanço geral (ponderado por custo)', f'=IFERROR(SUMPRODUCT(Etapas!H3:H{n + 1},Etapas!E3:E{n + 1})/SUM(Etapas!E3:E{n + 1}),0)', '', 'ponderado pela média da faixa de cada etapa'),
    ('Etapas concluídas', f'=COUNTIF(Etapas!G3:G{n + 1},"concluída")', f'de {len(etapas)}', ''),
]
for i, ln in enumerate(linhas, start=5):
    for j, v in enumerate(ln, start=1):
        c = ws.cell(row=i, column=j, value=v)
        if i == 5:
            c.font = Font(name='Arial', size=9, bold=True, color='FFFFFF')
            c.fill = PatternFill('solid', fgColor=AZUL)
        else:
            c.font = Font(name='Arial', size=10, bold=(j == 2), color=(AZUL if j == 2 else '1B2A3A'))
            c.border = BORDA
            c.alignment = Alignment(wrap_text=(j == 4), vertical='center')
ws['B7'].number_format = RS; ws['B8'].number_format = RS
ws['B9'].number_format = RS; ws['B10'].number_format = RS
ws['B11'].number_format = RS; ws['B12'].number_format = RS
ws['B14'].number_format = PCT

ws['A17'] = 'SISTEMA CONSTRUTIVO (revisão atual)'
ws['A17'].font = Font(name='Arial', size=11, bold=True, color=AZUL)
sist = [
    ('Paredes estruturais', 'Monolev ~340 m² líquidos — perímetro + térreo'),
    ('Divisórias do superior', 'Lightwall 2P 90 mm ~80 m² (conceito mezanino: telhado apoia só no perímetro)'),
    ('Lajes', 'Vigotas + EPS ~86 m² — SÓ pisos (superior, extensão, técnica). Não há laje de forro.'),
    ('Forro', 'Madeira acompanhando o telhado ~45 m² (mezanino + vão duplo) · gesso+EPS nivelado ~47 m² (demais)'),
    ('Cobertura', '3 treliças galvanizadas a fogo @3,25 m (banzos paralelos h=0,40, degrau triangulado) + terças Ue 100 · ~1,0 t'),
    ('Faixa NE', 'Área de luz descoberta até a fachada, dividida em 2 por parede cega: Luz 1 = jardim de inverno c/ parede verde e janelão 3,50; Luz 2 = varal/serve a lavanderia'),
    ('Fundação', 'Radier ~103 m²'),
]
for i, (a, b) in enumerate(sist, start=18):
    ws.cell(row=i, column=1, value=a).font = Font(name='Arial', size=9, bold=True, color=AZUL2)
    c = ws.cell(row=i, column=2, value=b); c.font = Font(name='Arial', size=9)
    ws.merge_cells(start_row=i, start_column=2, end_row=i, end_column=4)
    c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.row_dimensions[i].height = 24

ws['A27'] = 'COMO USAR'
ws['A27'].font = Font(name='Arial', size=11, bold=True, color=AZUL)
ws['A28'] = ('Esta planilha é um EXPORT do painel de obra e é regerada a cada cotação lançada no site. '
             'Edições feitas aqui serão perdidas na próxima geração — lance tudo pelo site '
             '(pvizioli.github.io/projeto_casa_pedro) para que vire commit e volte para cá.')
ws['A28'].font = Font(name='Arial', size=9, italic=True, color=AMBAR)
ws.merge_cells('A28:D30'); ws['A28'].alignment = Alignment(wrap_text=True, vertical='top')

# ============================ 2 · ETAPAS ============================
ws = wb.create_sheet('Etapas')
ws['A1'] = 'ETAPAS DA OBRA — 13 FASES'
ws['A1'].font = Font(name='Arial', size=13, bold=True, color=AZUL)
cabecalho(ws, 2, ['#', 'Etapa', 'Estim. baixa', 'Estim. alta', 'Média', '% do total',
                  'Status', 'Avanço', 'Custo real', 'Cotado', 'Δ vs. alta', 'Observação'],
          [5, 34, 13, 13, 13, 9, 13, 9, 13, 13, 13, 52])
nc = max(len(cots) + 1, 2)
STATUS = {'nao_iniciada': 'não iniciada', 'em_andamento': 'em andamento', 'concluida': 'concluída'}
for i, e in enumerate(etapas):
    r = 3 + i
    corpo(ws, r, [e['id'], e['nome'], e['estimativa_baixa'], e['estimativa_alta'],
                  f'=(C{r}+D{r})/2', f'=IFERROR(E{r}/$E${n + 2},0)', STATUS[e['status']],
                  e['progresso'] / 100, e['custo_real'],
                  f'=SUMIFS(Cotações!$J$2:$J${nc},Cotações!$F$2:$F${nc},$A{r})',
                  f'=IF(J{r}=0,"",D{r}-J{r})', e['obs']],
          fmt={3: RS, 4: RS, 5: RS, 6: PCT, 8: PCT, 9: RS, 10: RS, 11: RS})
r = n + 2
ws.cell(row=r, column=2, value='TOTAL').font = Font(name='Arial', size=10, bold=True, color=AZUL)
for col, f in ((3, f'=SUM(C3:C{r - 1})'), (4, f'=SUM(D3:D{r - 1})'), (5, f'=SUM(E3:E{r - 1})'),
               (9, f'=SUM(I3:I{r - 1})'), (10, f'=SUM(J3:J{r - 1})')):
    c = ws.cell(row=r, column=col, value=f)
    c.font = Font(name='Arial', size=10, bold=True, color=AZUL); c.number_format = RS
    c.border = Border(top=Side(style='thin', color=AZUL))
ws.cell(row=r, column=6, value='100%').font = Font(name='Arial', size=10, bold=True, color=AZUL)

# ============================ 3 · ITENS ============================
ws = wb.create_sheet('Itens')
ws['A1'] = 'CATÁLOGO DE ITENS COTÁVEIS'
ws['A1'].font = Font(name='Arial', size=13, bold=True, color=AZUL)
ws['A2'] = 'Base do formulário de cotação do site. Quantidades = memória de cálculo do projeto.'
ws['A2'].font = Font(name='Arial', size=8, italic=True, color='5A6B7D')
cabecalho(ws, 3, ['ID', 'Categoria', 'Item', 'Especificação', 'Un', 'Qtde',
                  'Nº cotações', 'Melhor preço unit.', 'Melhor total', 'Observação'],
          [7, 17, 42, 46, 6, 9, 10, 14, 14, 52])
for i, it in enumerate(itens):
    r = 4 + i
    corpo(ws, r, [it['id'], it['categoria'], it['item'], it.get('especificacao') or '',
                  it.get('unidade') or '', it.get('quantidade'),
                  f'=COUNTIFS(Cotações!$D$2:$D${nc},$A{r})',
                  f'=IF(G{r}=0,"—",_xlfn.MINIFS(Cotações!$I$2:$I${nc},Cotações!$D$2:$D${nc},$A{r}))',
                  f'=IF(G{r}=0,"—",IFERROR(H{r}*F{r},""))',
                  it.get('obs') or ''],
          fmt={6: '#,##0.00', 8: RS2, 9: RS})

# ============================ 4 · COTAÇÕES ============================
ws = wb.create_sheet('Cotações')
cabecalho(ws, 1, ['ID', 'Data', 'Categoria', 'Item ID', 'Item', 'Etapa', 'Fornecedor',
                  'Qtde', 'Preço unit.', 'Total', 'Melhor?', 'Observação'],
          [7, 11, 17, 8, 40, 7, 22, 9, 13, 13, 9, 44])
if cots:
    for i, c_ in enumerate(cots):
        r = 2 + i
        corpo(ws, r, [c_['id'], c_.get('data'), c_.get('categoria'), c_.get('item_id'), c_.get('item'),
                      c_.get('etapa'), c_.get('fornecedor'), c_.get('quantidade'), c_.get('preco_unit'),
                      f'=H{r}*I{r}',
                      f'=IF(I{r}=_xlfn.MINIFS($I$2:$I${nc},$D$2:$D${nc},$D{r}),"SIM","")',
                      c_.get('obs') or ''],
              fmt={8: '#,##0.00', 9: RS2, 10: RS})
else:
    ws['A3'] = 'Nenhuma cotação lançada ainda — use o formulário do site.'
    ws['A3'].font = Font(name='Arial', size=9, italic=True, color=AMBAR)
    ws.merge_cells('A3:L3')

# ============================ 5 · COMPARATIVO ============================
ws = wb.create_sheet('Comparativo')
ws['A1'] = 'COTADO × ESTIMADO POR ETAPA'
ws['A1'].font = Font(name='Arial', size=13, bold=True, color=AZUL)
cabecalho(ws, 2, ['#', 'Etapa', 'Estim. baixa', 'Estim. alta', 'Real / cotado', 'Δ vs. alta', 'Situação'],
          [5, 36, 14, 14, 14, 14, 26])
for i, e in enumerate(etapas):
    r = 3 + i; er = 3 + i
    corpo(ws, r, [e['id'], e['nome'], f'=Etapas!C{er}', f'=Etapas!D{er}',
                  f'=IF(Etapas!I{er}>0,Etapas!I{er},Etapas!J{er})',
                  f'=IF(E{r}=0,"",D{r}-E{r})',
                  f'=IF(E{r}=0,"sem cotação",IF(E{r}>D{r},"ACIMA da faixa",IF(E{r}<C{r},"abaixo da faixa","dentro da faixa")))'],
          fmt={3: RS, 4: RS, 5: RS, 6: RS})

# ============================ 6 · REVISÕES ============================
ws = wb.create_sheet('Revisões')
ws['A1'] = 'HISTÓRICO DE REVISÕES DO PROJETO'
ws['A1'].font = Font(name='Arial', size=13, bold=True, color=AZUL)
cabecalho(ws, 2, ['Data', 'Alteração', 'Impacto'], [12, 62, 62])
revs = [
    ('13/07/2026', 'Versão inicial da planilha (13 etapas, 116 itens)', 'Faixa R$ 498–764 mil'),
    ('13/07/2026', 'Orientação corrigida: frente NOROESTE (não norte)', 'Fachada frontal recebe sol da tarde — verificar conforto'),
    ('13/07/2026', 'Janelão da escada c/ peitoril 1,00 m (2,2 × 4,70)', 'Vidro 12 → 10,5 m²'),
    ('13/07/2026', 'Vão da garagem em altura total (chão → laje), viga na testada', 'Perfil da viga a validar (altura útil limitada)'),
    ('15/07/2026', 'Esclarecido: lajes = SÓ pisos. Forro nivelado gesso+EPS incluído', '+47 m² de forro (antes ausente do orçamento)'),
    ('15/07/2026', 'Forro de MADEIRA no mezanino/vão duplo acompanhando o telhado', '+45 m² · R$ 8–16 mil (item premium)'),
    ('15/07/2026', 'Divisórias do superior migradas de Monolev p/ Lightwall 2P 90', 'Monolev 421 → 340 m² · Etapa 4: R$ 120–170k → R$ 110–156k'),
    ('16/07/2026', 'Faixa NE: área de luz até a fachada, portinha recuada 0,80', 'Telha 105 → 98 m² · estrutura 100 → 95 m²'),
    ('16/07/2026', 'Parede cega entre Luz 1 e Luz 2 · Luz 1 = jardim de inverno', '+14 m² parede verde · +12 m² janelão · impermeabilizar divisa'),
    ('16/07/2026', 'Cobertura: pórticos de viga cheia → 3 TRELIÇAS @3,25 m', 'Aço 1,4 t → ~1,0 t · degrau do lanternim triangulado'),
    ('16/07/2026', 'Terças: 6 → 4 linhas e Ue 150 → Ue 100', '−170 kg · σ 61 MPa (24% de fy), flecha L/483'),
]
for i, (d, a, imp) in enumerate(revs):
    corpo(ws, 3 + i, [d, a, imp])

wb.save(SAIDA)
print(f'OK · {SAIDA.name} · {len(etapas)} etapas · {len(itens)} itens · {len(cots)} cotações')
