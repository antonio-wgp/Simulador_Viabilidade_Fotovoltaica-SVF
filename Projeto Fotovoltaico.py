import pandas as pd
import math
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.ticker as mticker
import matplotlib
matplotlib.use('TkAgg')
from flask import Flask, render_template, request, render_template_string
import io
import base64
import locale
locale.setlocale(locale.LC_COLLATE, 'pt_BR.UTF-8')

# Parâmetros de entrada variáveis
lista_graficos = ["a", "a", "a", "a", "a"]
repeticao = 0
potencia_modulo = 0
Cidade = 'Florianópolis'
rede = 0
cosip = 13
Concessionaria = 'Celes'
ano_instalação = 0
jan = 285
fev = 284
mar = 285
abr = 278
mai = 250
jun = 254
jul = 247
ago = 280
sep = 273
out = 274
nov = 282
dez = 0
media_kwh = 0
fluxo_caixa = 0
estados = []
lista_conta_de_luz_sem_geracao = []
lista_conta_de_luz_com_geração = []
lista_resultado_liquido = []
cidades_por_estado = []
meses_valores = []
num_modulos = 0
lista_consumo = []

# Bloco 1
planilha = pd.read_excel("cidades.xlsx")
estados = []

for i in range(planilha.shape[0]):
    estados.append(planilha.loc[i, "STATE"])
estados = list(set(estados))
estados.sort()

cidades_por_estado = []
for i in range(len(estados)):
    cidades_por_estado.append([])
for i in range(planilha.shape[0]):
    cidade = planilha.loc[i, "NAME"]
    estado = planilha.loc[i, "STATE"]
    for j in range(len(estados)):
        if estados[j] == estado:
            cidades_por_estado[j].append(cidade)
for i in range(len(cidades_por_estado)):
    cidades_por_estado[i] = sorted(cidades_por_estado[i], key=locale.strxfrm)

lista_concessionarias = []
planilha_concessionaria = pd.read_excel("TUSD E TE - B1 E B3.xlsx")
for k in range (1,planilha_concessionaria.shape[0],2):
    lista_concessionarias.append(planilha_concessionaria.loc[k,'Concessionária'])
print(lista_concessionarias)


###

app = Flask(__name__)
app.static_folder = 'assets'

@app.route('/')
def index():
    return render_template('Formulario.html', estados=estados, cidades_por_estado=cidades_por_estado, Concessionaria=lista_concessionarias)

@app.route('/submit', methods=['POST'])
def submit():
    global repeticao, lista_consumo,num_modulos,meses_valores,cidades_por_estado,lista_resultado_liquido,lista_conta_de_luz_com_geração,lista_conta_de_luz_sem_geracao, fluxo_caixa, estados,potencia_modulo,Cidade, rede, cosip, Concessionaria, ano_instalação, jan, fev, mar, abr,mai, jun, jul, ago, sep, out, nov,dez, media_kwh
    repeticao = 1
    potencia_modulo = int(request.form['potencia_modulo'])
    Cidade = request.form['Cidade']
    rede = int(request.form['rede'])
    cosip = int(request.form['cosip'])
    Concessionaria = request.form['Concessionaria']
    ano_instalação = int(request.form['ano_instalação'])
    jan = int(request.form['jan'])
    fev = int(request.form['fev'])
    mar = int(request.form['mar'])
    abr = int(request.form['abr'])
    mai = int(request.form['mai'])
    jun = int(request.form['jun'])
    jul = int(request.form['jul'])
    ago = int(request.form['ago'])
    sep = int(request.form['sep'])
    out = int(request.form['out'])
    nov = int(request.form['nov'])
    dez = int(request.form['dez'])
    media_kwh = int(request.form['media_kwh'])
    for i in range(12):
        if jan and fev and mar and abr and mai and jun and jul and ago and sep and out and nov and dez > 0:
            media_kwh = (jan + fev + mar + abr + mai + jun + jul + ago + sep + out + nov + dez) / 12
            lista_consumo = [jan, fev, mar, abr, mai, jun, jul, ago, sep, out, nov, dez]
        else:
            lista_consumo = [media_kwh for i in range(0, 12)]

    print('Média anual de Kwh é de', media_kwh, 'KwH')
    print(lista_consumo)
    # Valores Fixos
    media_kwh_ano = media_kwh * 12
    aumento_consumo = 0.005
    taxa_desempenho = 0.8
    inflacao_tarifaria = 0.06  # aumento do custo da tarifa 6% ao ano
    decaimento_anual = 0.005  # decaimento da geração das placas 0,5% ao ano
    manutencao = 0.01  # será alterado para cada tipo de sistema
    TMA = 0.1  # taxa minima de atratividade
    icms = 0.12  # Imposto sobre Circulação de Mercadorias e Serviços (vária a cada estado)
    PIS = 0.0065
    COFINS = 0.076
    taxa_simultaneidade = 0.7


    # Bloco 2
    # Leitura dos dados de irradiação solar para diferentes meses em várias cidades
    cidades = pd.read_excel('cidades.xlsx')  # apenas lê o excel
    cidade_tamanho = cidades.shape[0]  # shape[0] lê todas as linhas do excel

    meses_nome = ["ANNUAL", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    meses_valores = []
    for cidade in range(cidade_tamanho):
        if cidades.loc[cidade, 'NAME'] == Cidade:  # nome da cidade nos parâmetros de entrada variável
            for mes in range(len(meses_nome)):  # busca o tamanho da lista
                meses_valores.append(cidades.loc[cidade, meses_nome[mes]])

    # Irradiação (kWh/m²) - será feito um cálculo mais preciso futuramente
    irradiacao = meses_valores[0] / 1000  # usa a irradiação 'Annual'. divide por 1000 para obter (kWh/m²)
    ##
    # Bloco 3
    # TE e TUDS de cada concessionária
    planilha_impostos = pd.read_excel("TUSD E TE - B1 E B3.xlsx")
    impostos_tamanho = planilha_impostos.shape[0]
    impostos_nome = ['Concessionária', 'Resolução ANEEL', 'Início Vigência', 'Fim Vigência',
                     'Base Tarifária', 'Subgrupo', 'Classe', 'Unidade', 'TUDS', 'TE']
    impostos_valores = []
    for imposto in range(impostos_tamanho):
        if planilha_impostos.loc[imposto, 'Concessionária'] == Concessionaria:
            TUDS = planilha_impostos.loc[imposto, 'TUDS']
            print('o TUDS da sua concessionária de é', TUDS, 'o KwH')
            TE = planilha_impostos.loc[imposto, 'TE']
            print('o TE da sua concessionária de é', TE, 'o KwH')

    # Para calcular a taxa de disponibilidade
    if rede == 3:
        fornecimento_energia = 100
    elif rede == 2:
        fornecimento_energia = 50
    elif rede == 1:
        fornecimento_energia = 30
    else:
        print('Erro')

    # Cálculo do FioB
    planilha_FioB = pd.read_excel("FIO B - B1 E B3.xlsx")
    fiob_tamanho = planilha_FioB.shape[0]
    fiob_nome = ['Concessionária', 'Classe', 'Unidade', 'Fio_B', 'Valor']
    fio_b_valores = [0.15, 0.30, 0.45, 0.60, 0.75, 0.90]
    Valor_Fio_B_ano = 0
    for fiob in range(fiob_tamanho):
        if planilha_FioB.loc[fiob, 'Concessionária'] == Concessionaria:
            Valor_Fio_B = planilha_FioB.loc[fiob, 'Valor']
            if ano_instalação == 2023:
                Valor_Fio_B_ano = (Valor_Fio_B) * 0.15
            elif ano_instalação == 2024:
                Valor_Fio_B_ano == (Valor_Fio_B) * 0.30
            elif ano_instalação == 2025:
                Valor_Fio_B_ano = (Valor_Fio_B) * 0.45
            elif ano_instalação == 2026:
                Valor_Fio_B_ano = (Valor_Fio_B) * 0.60
            elif ano_instalação == 2027:
                Valor_Fio_B_ano = (Valor_Fio_B) * 0.75
            elif ano_instalação == 2028:
                Valor_Fio_B_ano = (Valor_Fio_B) * 0.90
            else:
                Valor_Fio_B_ano = (Valor_Fio_B) * 1

    print('O valor do Fio B será de ', Valor_Fio_B_ano, 'o KwH')

    # Cálculo de geração de cada placa por mês
    geracao_placa = (((potencia_modulo) * (irradiacao) * 30) / 1000) * 0.8

    # pfv (potência pico que o sistema deve gerar para atender a demanda do local) - em KwP
    pfv = (media_kwh) / ((irradiacao) * 30 * (taxa_desempenho))
    print('potencia fotovoltaica de', pfv)

    # Calcular número de módulos
    num_modulos = math.ceil(pfv / (potencia_modulo / 1000))  # Numero será arredondado para cima

    # Biblioteca de placas
    if potencia_modulo == 405:
        preco_modulos = 1100  # valor em R$
        area_placa = 1.9  # m²
    elif potencia_modulo == 550:
        preco_modulos = 1500
        area_placa = 2.6
    elif potencia_modulo == 700:
        preco_modulos = 1500
        area_placa = 2.6
    else:
        print('Potência de placa não cadastrada')
    ocupacao_total_telhado = num_modulos * area_placa
    print('O telhado deverá possuir um mínimo de', (ocupacao_total_telhado * (1 + 0.15)), 'm² de área')

    # Biblioteca de inversor
    # Inversor deve ser menor que a potência em kwh (até 25%) para funcionar melhor
    potencia_inversor = ((num_modulos) * (potencia_modulo)) / 1000  # Kwp

    print('Potência do inversor será de', potencia_inversor, 'Kw')

    planilha_inversores = pd.read_excel("Pasta1.xlsx")
    num_inversores = planilha_inversores.shape[0]

    for inversor in range(num_inversores):
        if planilha_inversores.loc[inversor, "POTÊNCIA (CA)"] * 1.25 > potencia_inversor:
            print("Inversor: ", planilha_inversores.loc[inversor, "DESCRIÇÃO GERAL"])
            print("Preço: ", planilha_inversores.loc[inversor, "Custo do Inv. (R$)"])
            preco_inversor = planilha_inversores.loc[inversor, "Custo do Inv. (R$)"]
            break  # interrompe o looping quando achar a primeira entrada

    num_inversor = 1

    # Geração mensal total (em kwh) e geração anual do primeiro ano
    geracao_mensal_total = (num_modulos) * (geracao_placa)
    geracao_ano_0 = math.ceil((geracao_mensal_total) * 12)

    # Custo dos módulos e inversores
    custo_modulo = (num_modulos) * (preco_modulos)
    custo_inversor = (num_inversor) * (preco_inversor)

    # Custo total do projeto
    investimento_total = (custo_modulo + custo_inversor) + ((custo_modulo + custo_inversor) * 0.3)

    # Tarifa sem impostos
    tarifa_bruta = TE + TUDS

    # Tarifa com os impostos
    tarifa = (tarifa_bruta) / (1 - PIS - COFINS) / (1 - icms)  # equação retirada do site da celesc

    # Valor somado a conta de luz que depende da quantia de fases
    taxa_disponibilidade = (fornecimento_energia * tarifa) * 12

    conta_de_luz_com_geracao = 0
    geracao_anual = 0
    aumento_consumo_ano = 0
    fluxo_caixa = [-investimento_total]
    lista_resultado_liquido = [-investimento_total]
    lista_resultado_liquido_corrigido = []
    lista_tarifa_corrigida = []
    lista_conta_de_luz_com_geração = []
    lista_geracao_anual = []
    lista_fiob_real = []
    lista_consumo_anual = []
    lista_conta_de_luz_sem_geracao = []

    index = [i for i in range(ano_instalação - 2023, 6)]

    for ano in range(1, 26):
        # Valor da conta de luz sem a geração solar
        tarifa_corrigida = (tarifa + (tarifa * inflacao_tarifaria * (ano - 1)))
        conta_de_luz_real = ((tarifa_corrigida * media_kwh_ano) + (cosip * 12))
        lista_conta_de_luz_sem_geracao.append(conta_de_luz_real)

        VPL = (1 + TMA) ** (ano - 1)

        preco_inversor_corrigido = preco_inversor + (preco_inversor * inflacao_tarifaria * (ano - 1))
        decaimento_geração = ((geracao_ano_0 * decaimento_anual) * (ano - 1))
        consumo_anual = (media_kwh_ano) + (media_kwh_ano * aumento_consumo * (ano - 1))
        geracao_anual = (geracao_ano_0 - decaimento_geração)
        receita = geracao_anual * tarifa_corrigida
        lista_geracao_anual.append(geracao_anual)
        lista_consumo_anual.append(consumo_anual)

        if len(index) >= ano:

            # Valor do fiob de cada ano (até 2028)
            fiobaneel = Valor_Fio_B * fio_b_valores[index[ano - 1]]

            # Valor do fiob corrigido com os impostos
            fiob_imposto = fiobaneel / (1 - PIS - COFINS) / (1 - icms)  # com a variação do fio b
            fiob_imposto1 = Valor_Fio_B / (1 - PIS - COFINS) / (1 - icms)  # sem a variação do fio b

            print(fio_b_valores[index[ano - 1]])
            fiob_real = ((geracao_ano_0 - decaimento_geração) * taxa_simultaneidade) * \
                        (fiob_imposto + (fiob_imposto * inflacao_tarifaria * (ano - 1)))
            lista_fiob_real.append(fiob_real)

        else:
            fiob_imposto1 = (Valor_Fio_B) / (1 - PIS - COFINS) / (1 - icms)

            fiob_real = ((geracao_ano_0 - decaimento_geração) * taxa_simultaneidade) * \
                        (fiob_imposto1 + (fiob_imposto1 * inflacao_tarifaria * (ano - 1)))

        if taxa_disponibilidade > fiob_real:
            conta_de_luz_com_geracao = ((taxa_disponibilidade) + (cosip * 12) + ((consumo_anual - geracao_anual) *
                                                                                 tarifa_corrigida))
            print("Taxa de disponibilidade")
        if fiob_real > taxa_disponibilidade:
            conta_de_luz_com_geracao = (
                        (fiob_real) + (cosip * 12) + ((consumo_anual - geracao_anual) * tarifa_corrigida))
            print("Fiob real")

        resultado_bruto = conta_de_luz_real
        resultado_liquido = resultado_bruto - conta_de_luz_com_geracao
        # Compra de inversor nos anos 10 e 20
        if ano == 11 or ano == 21:
            resultado_liquido -= preco_inversor
        resultado_liquido_corrigido = resultado_liquido / (1 + TMA) ** (ano - 1)

        lista_resultado_liquido.append(resultado_liquido)  # lista resultado liquido
        fluxo_caixa.append(resultado_liquido_corrigido + fluxo_caixa[len(fluxo_caixa) - 1])  # lista do fluxo de caixa
        lista_resultado_liquido_corrigido.append(resultado_liquido_corrigido)  # lista resultado liquido corrigido
        lista_tarifa_corrigida.append(tarifa_corrigida)  # lista tarifa corrigida
        lista_conta_de_luz_com_geração.append(conta_de_luz_com_geracao)  # lista conta de luz com geração

    print('Valor do Fio B real será de', lista_fiob_real)
    print('resultado liquido', lista_resultado_liquido)
    print('resultado liquido corrigido', lista_resultado_liquido_corrigido)
    print('o fluxo de caixa será de', fluxo_caixa)
    print('A conta anual com a geração será de R$', lista_conta_de_luz_com_geração)
    print('a conta de luz sem geração é de R$', lista_conta_de_luz_sem_geracao)
    print('tarida corrigida', lista_tarifa_corrigida)
    print('O valor da tarifa será de', tarifa)
    print('A Geração das placas solares será de', geracao_ano_0, 'KwH do primeiro ano')
    print(Valor_Fio_B_ano)
    print('O investimento do projeto será de R$', investimento_total)
    print(lista_geracao_anual)
    print(geracao_ano_0)
    print(lista_consumo_anual)
    print('O número de modulos será de',num_modulos)

    # Calcular o TIR (Taxa Interna de Retorno)
    tir = npf.irr(lista_resultado_liquido)
    print("Taxa Interna de Retorno (TIR): {:.2%}".format(tir))
    print(num_modulos)
    imagem1()
    imagem2()
    imagem3()
    imagem4()
    return render_template_string('''
        <head>
            <link rel="stylesheet" type="text/css" href="styles.css">
        </head>
        <style>
            body {
                margin: 400px 0 0; /* Adicionando margem no topo para deixar espaço para o cabeçalho */
                padding: 0;
                overflow-y: auto;
                background-image:
                    url("{{ url_for('static', filename='fundoinicial.png') }}"),
                    url("{{ url_for('static', filename='fundomeio1.png') }}"),
                    url("{{ url_for('static', filename='fundomeio2.png') }}"),
                    url("{{ url_for('static', filename='fundomeio3.png') }}"),
                    url("{{ url_for('static', filename='fundofinal.png') }}");
                background-size: 100% auto; /* Cada imagem cobrirá 100% da largura e terá altura automática */
                background-repeat: no-repeat;
                background-position: center top, center 25%, center 50%, center 75%, center 100%; /* Posição para cada imagem */
                height: 500vh; /* Ajuste a altura conforme necessário para acomodar as quatro imagens */
            }
            /* Defina a transição de fade-in */
            .fade-in {
                opacity: 0;
                transform: translateY(20px);
                transition: opacity 0.6s ease, transform 0.6s ease;
            }
        
            /* Quando o elemento é visível, aplique a animação */
            .fade-in.is-visible {
                opacity: 1;
                transform: translateY(0);
            }
            .content {
                display: flex;
                flex-direction: column;
                align-items: center;
                overflow-y: auto; /* Adicionado para permitir rolagem vertical */
            }

            .chart-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-bottom: 20px;
                min-height: 300px; /* Defina a altura mínima conforme necessário */
            }

            .chart-title {
                text-align: center;
                margin-bottom: 10px;
            }

            .chart-subtitle {
                text-align: center;
                margin-bottom: 5px;
            }

            .chart-description {
                text-align: left;
                max-width: 500px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
                margin-top: 10px; /* Adicionado para adicionar margem acima da descrição do gráfico */
            }
        </style>
        <body>
            
            <div class="content">
                <div class="chart-container fade-in">
                    <div class="chart-title">Título do Gráfico 1</div>
                    <img src="data:image/png;base64,{{ image_data1 }}" alt="Gráfico 1">
                    <div class="chart-subtitle">Subtítulo do Gráfico 1</div>
                    <div class="chart-description">
                        <p>Esta é uma caixa de texto onde você pode explicar o Gráfico 1 e editar o conteúdo.</p>
                    </div>
                </div>
    
                <div class="chart-container fade-in">
                    <div class="chart-title">Título do Gráfico 2</div>
                    <img src="data:image/png;base64,{{ image_data2 }}" alt="Gráfico 2">
                    <div class="chart-subtitle">Subtítulo do Gráfico 2</div>
                    <div class="chart-description">
                        <p>Esta é uma caixa de texto onde você pode explicar o Gráfico 2 e editar o conteúdo.</p>
                    </div>
                </div>
    
                <div class="chart-container fade-in">
                    <div class="chart-title">Título do Gráfico 3</div>
                    <img src="data:image/png;base64,{{ image_data3 }}" alt="Gráfico 3">
                    <div class="chart-subtitle">Subtítulo do Gráfico 3</div>
                    <div class="chart-description">
                        <p>Esta é uma caixa de texto onde você pode explicar o Gráfico 3 e editar o conteúdo.</p>
                    </div>
                </div>
                
                <div class="chart-container fade-in">
                    <div class="chart-title">Título do Gráfico 4</div>
                    <img src="data:image/png;base64,{{ image_data4 }}" alt="Gráfico 4">
                    <div class="chart-subtitle">Subtítulo do Gráfico 4</div>
                    <div class="chart-description">
                        <p>Esta é uma caixa de texto onde você pode explicar o Gráfico 4 e editar o conteúdo.</p>
                    </div>
                </div>
    
                <!-- Texto comum abaixo dos gráficos -->
                <div class="text-section">
                    <h2>Texto Geral Abaixo dos Gráficos</h2>
                    <p>Adicione o texto que deseja exibir abaixo dos gráficos.</p>
                </div>
            </div>
            <script>
                const elements = document.querySelectorAll('.fade-in');
    
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('is-visible');
                            observer.unobserve(entry.target);
                        }
                    });
                }, { threshold: 0.5 });
                
                elements.forEach((element) => {
                    observer.observe(element);
                });
            </script>
        </body>
        ''', image_data1=lista_graficos[1], image_data2=lista_graficos[2],
                                  image_data3=lista_graficos[3], image_data4=lista_graficos[4])

def imagem1():
    global lista_graficos, lista_consumo,num_modulos,meses_valores,cidades_por_estado,lista_resultado_liquido,lista_conta_de_luz_com_geração,lista_conta_de_luz_sem_geracao, fluxo_caixa, estados,potencia_modulo,Cidade, rede, cosip, Concessionaria, ano_instalação, jan, fev, mar, abr,mai, jun, jul, ago, sep, out, nov,dez, media_kwh

    fig, ax = plt.subplots(figsize=(12, 6))
    anos = [ano for ano in range(0, 26)]
    bars = ax.bar(anos, fluxo_caixa, width=0.6, align='center')

    for bar, valor in zip(bars, fluxo_caixa):
        cor_texto = 'red' if valor < 0 else 'green'
        va = 'top' if valor < 0 else 'bottom'
        fontsize = 9
        shadow = pe.withStroke(linewidth=2, foreground='white')
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{valor:.2f}', ha='center', va=va,
                rotation=90, color=cor_texto, fontsize=fontsize, path_effects=[shadow])
    ax.set_ylim(min(fluxo_caixa) * 1.6, max(fluxo_caixa) * 1.6)
    ax.set_title('Payback Descontado do Projeto Fotovoltaico', fontsize=14)
    ax.set_xlabel('Ano', fontsize=12)
    ax.set_ylabel('Fluxo de Caixa (R$)', fontsize=12)
    def currency(x, pos):
        return 'R$ {:.2f}'.format(x)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(currency))
    # Definindo as cores das barras conforme o sinal dos valores
    for bar, valor in zip(bars, fluxo_caixa):
        bar.set_color('red' if valor < 0 else 'green')
    ax.set_xticks(anos)
    fig.tight_layout()
    #plt.show()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    lista_graficos[1] = (base64.b64encode(buffer.read()).decode())

def imagem2():
    global lista_graficos, lista_consumo,num_modulos,meses_valores,cidades_por_estado,lista_resultado_liquido,lista_conta_de_luz_com_geração,lista_conta_de_luz_sem_geracao, fluxo_caixa, estados,potencia_modulo,Cidade, rede, cosip, Concessionaria, ano_instalação, jan, fev, mar, abr,mai, jun, jul, ago, sep, out, nov,dez, media_kwh, image_data
    # Largura das colunas
    anos = list(range(0, 25))
    largura = 0.4

    pos_conta_sem_geracao = np.arange(len(anos))
    pos_conta_com_geracao = [pos + largura for pos in pos_conta_sem_geracao]

    plt.figure(figsize=(10, 6))
    plt.bar(pos_conta_sem_geracao, lista_conta_de_luz_sem_geracao, width=largura, label='Conta sem Geração')
    plt.bar(pos_conta_com_geracao, lista_conta_de_luz_com_geração, width=largura, label='Conta com Geração', alpha=0.7)
    plt.xlabel('Ano')
    plt.ylabel('Valor da Conta de Luz (R$)')
    plt.title('Comparação da Conta de Luz com e sem Geração de Energia Solar')
    plt.xticks([pos + largura / 2 for pos in pos_conta_sem_geracao], anos)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    #plt.show()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    lista_graficos[2] = (base64.b64encode(buffer.read()).decode())

def imagem3():
    global lista_graficos, lista_consumo,num_modulos,meses_valores,cidades_por_estado,lista_resultado_liquido,lista_conta_de_luz_com_geração,lista_conta_de_luz_sem_geracao, fluxo_caixa, estados,potencia_modulo,Cidade, rede, cosip, Concessionaria, ano_instalação, jan, fev, mar, abr,mai, jun, jul, ago, sep, out, nov,dez, media_kwh, image_data
    # Dados do gráfico
    anos = [ano for ano in range(0, 26)]

    # Margens personalizadas
    margem_inferior = min(lista_resultado_liquido) * 1.5  # Ajuste o valor conforme necessário
    margem_superior = max(lista_resultado_liquido) * 3  # Ajuste o valor conforme necessário

    # Criar figura e eixo para o gráfico
    fig, ax = plt.subplots(figsize=(12, 6))

    # Criar o gráfico de barras com cores personalizadas
    cores = ['red' if valor < 0 else 'green' for valor in lista_resultado_liquido]
    bars = ax.bar(anos, lista_resultado_liquido, width=0.6, align='center', color=cores)

    # Adicionar valores acima das barras
    for bar, valor in zip(bars, lista_resultado_liquido):
        cor_texto = 'black'
        va = 'bottom' if valor >= 0 else 'top'
        fontsize = 9
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{valor:.2f}', ha='center', va=va,
                rotation=90, color=cor_texto, fontsize=fontsize,
                path_effects=[pe.withStroke(linewidth=3, foreground='white')])

    # Configurar margem inferior e superior
    ax.set_ylim(bottom=margem_inferior, top=margem_superior)

    # Definindo o título e os rótulos dos eixos
    ax.set_title('Fluxo de Caixa do Projeto Fotovoltaico', fontsize=14)
    ax.set_xlabel('Ano', fontsize=12)
    ax.set_ylabel('Fluxo de Caixa (R$)', fontsize=12)

    # Formatando o eixo y como valores monetários
    def currency(x, pos):
        return 'R$ {:.2f}'.format(x)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(currency))
    ax.set_xticks(anos)

    # Ajustando o layout do gráfico
    fig.tight_layout()
    # Exibindo o gráfico
    #plt.show()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    lista_graficos[3] = base64.b64encode(buffer.read()).decode()

def imagem4():
    global lista_graficos, lista_consumo,num_modulos,meses_valores,cidades_por_estado,lista_resultado_liquido,lista_conta_de_luz_com_geração,lista_conta_de_luz_sem_geracao, fluxo_caixa, estados,potencia_modulo,Cidade, rede, cosip, Concessionaria, ano_instalação, jan, fev, mar, abr,mai, jun, jul, ago, sep, out, nov,dez, media_kwh, image_data
    # Gráfico da Geração e Consumo Mensal do Conjunto de Placas Solares
    # Gráfico da Geração Mensal do Conjunto de Placas Solares
    geracao_conjunto_mes = []
    for mes in range(1, 13):
        irradiacao_mes = meses_valores[mes] / 1000
        geracao_mes = (((potencia_modulo) * (irradiacao_mes) * 30) / 1000) * 0.75
        geracao_conjunto_mes.append(geracao_mes * num_modulos)
    print(geracao_conjunto_mes)

    meses = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
    for i in range(4):
        plt.clf()
    plt.figure(figsize=(10, 6))
    bar_width = 0.4
    plt.bar(np.arange(len(meses)), geracao_conjunto_mes, bar_width, color='b', label='Geração de Energia')
    plt.bar(np.arange(len(meses)) + bar_width, lista_consumo, bar_width, color='orange', label='Consumo de Energia')
    plt.xlabel('Mês')
    plt.ylabel('Energia (KWh)')
    plt.title('Geração e Consumo Mensal de Energia')
    plt.xticks(np.arange(len(meses)) + bar_width / 2, meses)
    plt.legend()
    plt.grid(True, linestyle='None')
    plt.tight_layout()
    #plt.show()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    lista_graficos[4] = base64.b64encode(buffer.read()).decode()

if __name__ == '__main__':
    app.run(debug=True)

