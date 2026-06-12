import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página para o celular
st.set_page_config(page_title="Volmaker - Sistema Comercial", page_icon="🏭", layout="centered")

# --- DADOS PADRÃO DE FÁBRICA (Todos os seus itens originais estão aqui guardados) ---
dados_padrao_maq = {
    "Categoria": ["Envasadoras", "Envasadoras", "Envasadoras", "Envasadoras", "Envasadoras", "Envasadoras", "Envasadoras", "Envasadoras", "Tampadoras", "Tampadoras", "Tampadoras", "Tampadoras", "Tampadoras", "Ensacadeiras", "Ensacadeiras", "Ensacadeiras", "Ensacadeiras", "Detector de Furos", "Detector de Furos", "Posicionadores e Elevadores", "Posicionadores e Elevadores", "Posicionadores e Elevadores", "Posicionadores e Elevadores", "Posicionadores e Elevadores", "Posicionadores e Elevadores", "Posicionadores e Elevadores", "Administrador de Peso"],
    "Equipamento": ["ENVASADORA POR CELULA DE CARGA 4 BICOS 5L (PPZ)", "ENVASADORA POR CELULA DE CARGA 4 BICOS 20L (PPZ)", "ENVASADORA POR CELULA DE CARGA 4 BICOS 5L (INOX)", "ENVASADORA POR CELULA DE CARGA 4 BICOS 20L (INOX)", "ENVASADORA LINEAR GRAVIMÉTRICA (PPZ)", "ENVASADORA LINEAR GRAVIMÉTRICA (INOX)", "ENVASADORA LINEAR VOLUMÉTRICA 10 BICOS (INOX)", "ENVASADORA ROTATIVA CÉLULA DE CARGA MONOBLOCO 16/8", "TAMPADORA DE BALDES SLIM", "TAMPADORA DE BALDES COM ALIMENTAÇÃO AUTOMÁTICA DE TAMPAS", "TAMPADORA TANGENCIAL", "TAMPADORA PASSO A PASSO SEM ALIMENTADOR DE TAMPAS", "TAMPADORA LINEAR", "ENSACADEIRA AMPLA C/ SOLDA", "ENSACADEIRA AMPLA S/ SOLDA", "ENSACADEIRA SLIM C/SOLDA", "ENSACADEIRA SLIM S/ SOLDA", "DETECTOR DE FUROS MODELO GOLD", "DETECTOR DE FUROS MODELO SLIM", "POSICIONADOR DE FRASCOS PADRÃO", "POSICIONADOR DE FRASCOS COMPACTO", "POSICIONADOR DE FRASCOS MINI", "ELEVADOR DE FRASCOS COM SILO", "CARREGADOR DE PREFORMA MOD. SC-001", "ELEVADOR DE TAMPAS", "ELEVADOR SELECIONADOR DE TAMPAS", "ADMINISTRADOR DE PESO"],
    "Preco": [131450.00, 157635.00, 131450.00, 157635.00, 193310.00, 193310.00, 317121.00, 1060250.00, 121159.00, 213600.00, 127422.00, 151810.00, 77550.00, 172146.00, 137122.00, 146333.00, 119218.00, 71633.00, 53396.00, 147239.00, 137111.00, 109213.00, 73202.00, 77190.00, 37412.00, 93141.00, 189500.00]
}
df_padrao_maq = pd.DataFrame(dados_padrao_maq)

dados_padrao_kits = {
    "Equipamento": ["PENTE DA ENVASADORA 12 BICOS", "BICO DE AÇO INOXIDÁVEL ATÉ PCO 28MM", "BICO DE AÇO INOXIDÁVEL ACIMA DE PCO 28MM"],
    "Preco": [10320.00, 1452.00, 1742.40]
}
df_padrao_kits = pd.DataFrame(dados_padrao_kits)

# --- TENTATIVA DE CONEXÃO COM O GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        df_maq = conn.read(worksheet="Maquinas", ttl=2)
        if df_maq.empty or "Equipamento" not in df_maq.columns:
            df_maq = df_padrao_maq
    except:
        df_maq = df_padrao_maq
        
    try:
        df_kits = conn.read(worksheet="Kits", ttl=2)
        if df_kits.empty or "Equipamento" not in df_kits.columns:
            df_kits = df_padrao_kits
    except:
        df_kits = df_padrao_kits
except Exception as e:
    df_maq = df_padrao_maq
    df_kits = df_padrao_kits

# Garantir formatação numérica correta
df_maq["Preco"] = pd.to_numeric(df_maq["Preco"], errors='coerce').fillna(0.0)
df_kits["Preco"] = pd.to_numeric(df_kits["Preco"], errors='coerce').fillna(0.0)

categorias_comerciais = ["Envasadoras", "Tampadoras", "Ensacadeiras", "Detector de Furos", "Posicionadores e Elevadores", "Administrador de Peso", "Rotuladoras", "Robôs"]

# --- ESTADO DO CARRINHO ---
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

# --- PAINEL LATERAL ---
st.sidebar.header("⚙️ Configurações Comerciais")
modo_apresentacao = st.sidebar.toggle("👁️ Modo Apresentação (Esconder Interno)", value=False)

if not modo_apresentacao:
    st.sidebar.subheader("Margens por Segmento")
    m_limp = st.sidebar.number_input("Produtos de Limpeza (%)", value=0.0, step=1.0)
    m_alim = st.sidebar.number_input("Alimentício (%)", value=10.0, step=1.0)
    m_cosm = st.sidebar.number_input("Cosméticos (%)", value=15.0, step=1.0)
    m_pharma = st.sidebar.number_input("Farmacêutico (%)", value=30.0, step=1.0)
else:
    m_limp, m_alim, m_cosm, m_pharma = 0.0, 10.0, 15.0, 30.0

segmentos_opcoes = {
    "Padrão de Fábrica": 0.0,
    "Produtos de Limpeza": m_limp / 100,
    "Alimentício": m_alim / 100,
    "Cosméticos": m_cosm / 100,
    "Farmacêutico": m_pharma / 100
}

def formatar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

# --- INTERFACE DO USUÁRIO ---
st.title("🏭 Orçador Inteligente - Volmaker")

# Abas principais do aplicativo
aba_tabela, aba_linha = st.tabs(["🔍 Ver Tabela de Preços", "🛒 Montar Linha Completa"])

# --- ABA 1: CONSULTA RÁPIDA DE PREÇOS ---
with aba_tabela:
    st.markdown("### Lista Geral de Equipamentos e Valores")
    cat_filtro = st.selectbox("Filtrar por Categoria Comercial:", ["Todas"] + categorias_comerciais)
    
    if cat_filtro == "Todas":
        df_mostrar = df_maq.copy()
    else:
        df_mostrar = df_maq[df_maq["Categoria"] == cat_filtro].copy()
        
    # Formatando a tabela para exibição bonita e profissional
    df_mostrar_formatado = df_mostrar.copy()
    df_mostrar_formatado["Preco"] = df_mostrar_formatado["Preco"].apply(formatar_real)
    
    st.dataframe(df_mostrar_formatado, use_container_width=True, hide_index=True)

# --- ABA 2: CONFIGURADOR DE LINHA COMPLETA ---
with aba_linha:
    with st.expander("➕ Selecionar Máquina para a Linha", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            cat_sel = st.selectbox("Categoria da Máquina:", categorias_comerciais, key="cat_linha")
        with col2:
            modelos_filtrados = df_maq[df_maq["Categoria"] == cat_sel]["Equipamento"].tolist()
            mod_sel = st.selectbox("Modelo da Máquina:", modelos_filtrados if modelos_filtrados else ["Nenhum cadastrado"], key="mod_linha")
        
        if st.button("Adicionar Máquina à Composição"):
            if modelos_filtrados and mod_sel != "Nenhum cadastrado":
                preco_item = df_maq[df_maq["Equipamento"] == mod_sel]["Preco"].values[0]
                st.session_state.carrinho.append({"Item": mod_sel, "Preco": float(preco_item), "Tipo": "Máquina"})
                st.toast(f"{mod_sel} adicionado à linha!")
                st.rerun()

    with st.expander("➕ Adicionar Periférico ou Esteira Extra"):
        lista_opcionais = df_kits["Equipamento"].tolist()
        if lista_opcionais:
            kit_sel = st.selectbox("Selecione o Opcional:", lista_opcionais, key="kit_linha")
            if st.button("Adicionar Opcional à Composição"):
                preco_kit = df_kits[df_kits["Equipamento"] == kit_sel]["Preco"].values[0]
                st.session_state.carrinho.append({"Item": kit_sel, "Preco": float(preco_kit), "Tipo": "Kit"})
                st.toast(f"{kit_sel} adicionado à linha!")
                st.rerun()

    # --- LISTA DA PROPOSTA ATUAL ---
    st.markdown("### 📋 Composição da Linha Orçada")
    if not st.session_state.carrinho:
        st.info("Nenhum item adicionado à linha ainda. Escolha os equipamentos nos painéis acima.")
    else:
        itens_display = pd.DataFrame(st.session_state.carrinho)
        st.table(itens_display.assign(Preco=itens_display["Preco"].apply(formatar_real)))
        
        if st.button("🗑️ Limpar Toda a Linha"):
            st.session_state.carrinho = []
            st.rerun()
            
        st.markdown("---")
        segmento_sel = st.selectbox("Definir Segmento Técnico da Linha:", list(segmentos_opcoes.keys()))
        
        # Cálculos de fechamento
        subtotal_puro = sum(item["Preco"] for item in st.session_state.carrinho)
        porcentagem = segmentos_opcoes[segmento_sel]
        valor_segmento = subtotal_puro * porcentagem
        total_final = subtotal_puro + valor_segmento

        if modo_apresentacao:
            st.success(f"## **Valor Total da Linha: {formatar_real(total_final)}**")
            st.caption(f"Especificação técnica sob medida para o segmento {segmento_sel}.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Subtotal Puro", formatar_real(subtotal_puro))
            c2.metric(f"Adicional Segmento ({int(porcentagem*100)}%)", formatar_real(valor_segmento))
            c3.metric("Valor Sugerido Final", formatar_real(total_final))
            
