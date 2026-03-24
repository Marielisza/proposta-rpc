import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os

# 1. Banco de Dados de Custos (Baseado na tabela Dr. Fiscal)
dados_custo = {
    "limite": [70000, 150000, 300000, 450000, 600000, 850000, 1000000, 3000000],
    12: [2500.00, 2917.80, 11671.20, 14589.00, 17506.80, 23342.40, 26260.20, 29178.00],
    24: [3890.40, 5835.60, 11671.20, 14589.00, 17506.80, 23342.40, 26260.20, 29178.00],
    36: [5835.60, 8753.40, 11671.20, 14589.00, 17506.80, 23342.40, 26260.20, 29178.00],
    48: [7780.80, 11671.20, 15561.60, 19452.00, 23342.40, 31123.20, 35013.60, 38904.00],
    60: [9726.00, 14589.00, 19452.00, 24315.00, 29178.00, 38904.00, 43767.00, 48630.00]
}

# --- LÓGICA DE CÁLCULO ---
def buscar_custo_interno(valor, meses_ref):
    for i, limite in enumerate(dados_custo["limite"]):
        if valor <= limite:
            return dados_custo[meses_ref][i]
    return dados_custo[meses_ref][-1] # Retorna o último se exceder o limite

st.set_page_config(page_title="Gerador de Propostas RPC", layout="wide")
st.title("📄 Gerador de Propostas RPC - Dr. Fiscal")

# --- BARRA LATERAL (INPUTS) ---
st.sidebar.header("👤 Identificação")
consultor = st.sidebar.text_input("Consultor Responsável")
unidade = st.sidebar.text_input("Unidade")

st.sidebar.header("🏢 Dados do Cliente")
razao_social = st.sidebar.text_input("Razão Social")
cnpj = st.sidebar.text_input("CNPJ")

st.sidebar.header("💰 Parâmetros do Serviço")
valor_credito = st.sidebar.number_input("Faixa de Crédito (R$)", min_value=0.0, step=1000.0, format="%.2f")
meses = st.sidebar.selectbox("Quantidade de Meses do Diagnóstico", [12, 24, 36, 48, 60])

# CORREÇÃO: Limite alterado para 99 para evitar divisão por zero
percentual = st.sidebar.slider("Percentual da Unidade (%)", 0, 99, 25) / 100

parcelas = st.sidebar.number_input("Quantidade de Parcelas", 1, 12, 5)
vencimento = st.sidebar.text_input("Data do 1º Vencimento", value=datetime.today().strftime('%d/%m/%Y'))
horas_tecnicas = st.sidebar.number_input("Horas Técnicas (Informativo)", value=20)

# --- BOTÃO DE GERAÇÃO ---
if st.sidebar.button("Gerar Proposta Profissional"):
    if not razao_social or not consultor:
        st.error("Por favor, preencha a Razão Social e o Consultor.")
    else:
        bg_image_path = 'tela_inicial.png'
        if not os.path.exists(bg_image_path):
            st.error(f"Erro: O arquivo de imagem de fundo '{bg_image_path}' não foi encontrado. Certifique-se de que ele esteja no mesmo diretório do script.")
        else:
            custo_base = buscar_custo_interno(valor_credito, meses)
            # Cálculo: Custo / (1 - percentual unidade)
            total_servico = custo_base / (1 - percentual)
            valor_parcela = total_servico / parcelas

            # --- GERAÇÃO DO PDF ---
            pdf = FPDF()
            pdf.add_page()
            
            # Nota: Se os acentos do PDF ficarem estranhos, você precisará carregar uma fonte TTF aqui.
            # Exemplo: pdf.add_font("Arial", "", "arial.ttf", uni=True)
            
            pdf.image(bg_image_path, 0, 0, w=210, h=45) 

            # Estilo Texto Cabeçalho Dr. Fiscal
            pdf.set_text_color(255, 255, 255) # Texto branco
            pdf.set_font("Arial", 'B', 16)
            pdf.set_y(15)
            pdf.cell(0, 10, "PROPOSTA DE PRESTAÇÃO DE SERVIÇOS - RPC", ln=True, align='C')
            
            # Dados da Unidade e Consultor
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 10, f"Unidade: {unidade} | Consultor: {consultor}", ln=True, align='C')
            
            # Reset para texto preto
            pdf.set_text_color(0, 0, 0)
            pdf.set_y(50) # Pula para baixo da imagem de fundo
            
            # Tabela de Identificação
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(40, 8, "EMPRESA:", 1)
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 8, razao_social, 1, ln=True)
            
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(40, 8, "SERVIÇO:", 1)
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 8, "Retificacoes Das Declaracoes e Compensacoes Mensais", 1, ln=True)
            
            # Conteúdo Técnico
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "1. OBJETIVO E ESCOPO", ln=True)
            pdf.set_font("Arial", size=11)
            texto_escopo = (
                "O servico de Retificacoes e Procedimentos de Compensacao preve a retificacao "
                "de todas as obrigacoes fiscais acessorias necessarias para a correta habilitacao "
                "dos ativos e dos passivos identificados no trabalho de Diagnostico Tributario. "
                "Estao contempladas a retificacao de DCTF, ECF e EFD Contribuicoes."
            )
            # Substituímos acentos acima temporariamente para evitar quebras nativas no FPDF padrão.
            pdf.multi_cell(0, 7, texto_escopo)
            
            # Investimento
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "2. INVESTIMENTO E CONDICOES", ln=True)
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 8, f"Remuneracao Total: R$ {total_servico:,.2f}", ln=True)
            pdf.cell(0, 8, f"Forma de Pagamento: {parcelas} parcelas de R$ {valor_parcela:,.2f}", ln=True)
            pdf.cell(0, 8, f"Primeiro Vencimento: {vencimento}", ln=True)
            pdf.cell(0, 8, f"Horas Tecnicas Alocadas: {horas_tecnicas} horas", ln=True)
            pdf.cell(0, 8, f"Prazo para Finalizacao: 60 dias", ln=True) 

            # Rodapé de Validade
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 10, "Esta proposta tem validade de 3 dias uteis.", ln=True)

            # CORREÇÃO: Tratamento para fpdf moderno vs antigo
            try:
                pdf_output = bytes(pdf.output())
            except TypeError:
                pdf_output = pdf.output(dest='S').encode('latin-1')

            st.success("Cálculo realizado com sucesso!")
            st.download_button(
                label="📥 Baixar Proposta em PDF",
                data=pdf_output,
                file_name=f"Proposta_RPC_{razao_social}.pdf",
                mime="application/pdf"
            )
