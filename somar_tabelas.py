import pandas as pd

# Carregar as tabelas CSV
tabela1 = pd.read_excel('Global Horizontal.xlsx')
tabela2 = pd.read_excel('Plano Inclinado.xlsx')
print(tabela1.head())
print(tabela2.columns)

tabelas_merge = pd.merge(tabela1, tabela2, on=['LON', 'LAT'], how='inner')
print(tabelas_merge.columns)

meses = ['ANNUAL', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

for mes in meses:
    col_x = f'{mes}_x'  # Coluna na tabela1
    col_y = f'{mes}_y'  # Coluna na tabela2
    col_soma = f'soma_{mes}'  # Nome da nova coluna de soma
    tabelas_merge[col_soma] = (tabelas_merge[col_x] + tabelas_merge[col_y])/2

tabelas_merge.to_excel('cidades.xlsx', index=False)