import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Volmaker - Sistema Comercial", page_icon="🏭", layout="centered")

# ID da Planilha (extraído do seu link)
SHEET_ID = "1W32LRAXpKWTL37-DeZiiSwBRnb0qYoY08slv767yw5o"

def carregar_aba(nome_aba):
    try:
        # URL de exportação direta do Google Sheets (mais estável)
        url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba}"
        df = pd.read_csv(url_csv)
        
        # Limpeza básica de colunas vazias e espaços
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df.columns = df.columns.str.strip()
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a aba '{nome_aba}': {e}")
        return pd.DataFrame()

# Puxando os dados das abas
df_maq_raw = carregar_aba("Maquinas")
df_kits_raw = carregar_aba("Kits")
df_margens_raw = carregar_aba("Margens")

def limpar_preco(valor_str):
    if pd.isna(valor_str) or str(valor_str).lower() == 'nan' or str(valor_str).strip() == '':
        return 0.0
    limpo = str(valor_str).replace("R$", "").replace("r$", "").replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(limpo)
    except:
        return 0.0

# Processamento de dados
df_maq = df_maq_raw.copy()
if not df_maq.empty and "Equipamento" in df_maq.columns:
    df_maq["Preco"] = df_maq["Preco"].apply(limpar_preco)
else:
    df_maq = pd.DataFrame(columns=["Categoria", "Equipamento", "Preco"])

df_kits = df_kits_raw.copy()
if not df_kits.empty and "Equipamento" in df_kits.columns:
    df_kits["Preco"] = df_kits["Preco"].apply(limpar_preco)
else:
    df_kits = pd.DataFrame(columns=["Equipamento", "Preco"])

segmentos_opcoes = {"Padrão de Fábrica": 0.0}
if not df_margens_raw.empty and "Porte" in df_margens_raw.columns:
    for _, linha in df_margens_raw.iterrows():
        try:
            porte = str(linha["Porte"])
            pct = float(str(linha["Porcentagem"]).replace("%", "").replace(",", ".")) / 100
            segmentos_opcoes[porte] = pct
        except:
            continue

# Interface
st.title("🏭 Orçador Inteligente - Volmaker")

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

aba_tabela, aba_linha = st.tabs(["🔍 Tabela de Preços", "🛒 Montar Linha"])

with aba_tabela:
    st.dataframe(df_maq, use_container_width=True)

with aba_linha:
    if df_maq.empty:
        st.warning("Dados não carregados. Verifique a planilha.")
    else:
        # Lógica do carrinho permanece igual
        modelo = st.selectbox("Selecione a Máquina", df_maq["Equipamento"].tolist())
        if st.button("Adicionar"):
            preco = df_maq[df_maq["Equipamento"] == modelo]["Preco"].values[0]
            st.session_state.carrinho.append({"Item": modelo, "Preco": float(preco)})
            st.rerun()
            
        st.write("Linha atual:", st.session_state.carrinho)
        
