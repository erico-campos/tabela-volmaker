import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página para o celular
st.set_page_config(page_title="Volmaker - Sistema Comercial", page_icon="🏭", layout="centered")

# --- INSTANCIANDO DATA_FRAMES VAZIOS DE SEGURANÇA ---
df_padrao_maq = pd.DataFrame(columns=["Categoria", "Equipamento", "Preco"])
df_padrao_kits = pd.DataFrame(columns=["Equipamento", "Preco"])

# Configuração padrão caso a nova aba da planilha ainda não esteja criada
df_padrao_margens = pd.DataFrame({
    "Porte": ["Pequena Empresa", "Media Empresa", "Grande Empresa", "Multinacional"],
    "Porcentagem": [0.0, 10.0, 30.0, 150.0]
})

# --- TENTATIVA DE CONEXÃO COM O GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Lendo aba Maquinas
    try:
        df_maq = conn.read(worksheet="Maquinas", ttl=2)
        if df_maq.empty or "Equipamento" not in df_maq.columns:
            df_maq = df_padrao_maq
    except:
        df_maq = df_padrao_maq
        
    # Lendo aba Kits
    try:
        df_kits = conn.read(worksheet="Kits", ttl=2)
        if df_kits.empty or "Equipamento" not in df_kits.columns:
            df_kits = df_padrao_kits
    except:
        df_kits = df_padrao_kits

    # Lendo a NOVA aba Margens permanente
    try:
        df_margens = conn.read(worksheet="Margens", ttl=2)
        if df_margens.empty or "Porcentagem" not in df_margens.columns:
            df_margens = df_padrao_margens
    except:
        df_margens = df_padrao_margens
except Exception as e:
    df_maq = df_padrao_maq
    df_kits = df_padrao_kits
    df_margens = df_padrao_margens

# Tratamento numérico dos preços e margens
if not df_maq.empty and "Preco" in df_maq.columns:
    df_maq["Preco"] = pd.to_numeric(df_maq["Preco"], errors='coerce').fillna(0.0)
if not df_kits.empty and "Preco" in df_kits.columns:
    df_kits["Preco"] = pd.to_numeric(df_kits["Preco"], errors='coerce').fillna(0.0)
df_margens["Porcentagem"] = pd.to_numeric(df_margens["Porcentagem"], errors='coerce').fillna(0.0)

# Criando o dicionário de opções baseado no que está salvo na Planilha
segmentos_opcoes = {"Padrão de Fábrica (sem acrescentar porcentagem)": 0.0}
for _, linha in df_margens.iterrows():
    segmentos_opcoes[linha["Porte"]] = float(linha["Porcentagem"]) / 100

# Categorias comerciais
categorias_comerciais = ["Envasadoras", "Tampadoras", "Ensacadeiras", "Detector de Furos", "Posicionadores e Elevadores", "Administrador de Peso", "Rotuladoras", "Robôs"]

# --- ESTADO DO CARRINHO DE COMPRAS ---
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

# --- PAINEL LATERAL ---
st.sidebar.header("⚙️ Configurações Comerciais")
modo_apresentacao = st.sidebar.toggle("👁️ Modo Apresentação (Esconder Interno)", value=False)

if not modo_apresentacao:
    st.sidebar.info("💡 Suas margens agora estão salvas na planilha Google! Para alterá-las permanentemente, edite a aba 'Margens' lá no seu Drive.")
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Margens Atuais da Planilha")
    for porte, valor in segmentos_opcoes.items():
        if "Padrão" not in porte:
            st.sidebar.text(f"{porte}: {int(valor * 100)}%")

def formatar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

# --- INTERFACE DO USUÁRIO ---
st.title("🏭 Orçador Inteligente - Volmaker")

aba_tabela, aba_linha = st.tabs(["🔍 Ver Tabela de Preços", "🛒 Montar Linha Completa"])

# --- ABA 1: CONSULTA DE PREÇOS ---
with aba_tabela:
    st.markdown("### Lista Geral de Equipamentos Cadastrados")
    if df_maq.empty:
        st.warning("Nenhum equipamento encontrado na aba 'Maquinas' da sua planilha.")
    else:
        cat_filtro = st.selectbox("Filtrar por Categoria Comercial:", ["Todas"] + categorias_comerciais)
        df_mostrar = df_maq.copy() if cat_filtro == "Todas" else df_maq[df_maq["Categoria"] == cat_filtro].copy()
        
        if df_mostrar.empty:
            st.info(f"Nenhum equipamento cadastrado na categoria '{cat_filtro}'.")
        else:
            df_mostrar_formatado = df_mostrar.copy()
            df_mostrar_formatado["Preco"] = df_mostrar_formatado["Preco"].apply(formatar_real)
            st.dataframe(df_mostrar_formatado, use_container_width=True, hide_index=True)

# --- ABA 2: CONFIGURADOR DE LINHA ---
with aba_linha:
    if df_maq.empty:
        st.warning("Preencha sua Planilha Google primeiro para habilitar o montador de linhas.")
    else:
        with st.expander("➕ Selecionar Máquina para a Linha", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                cat_sel = st.selectbox("Categoria da Máquina:", categorias_comerciais, key="cat_linha")
            with col2:
                modelos_filtrados = df_maq[df_maq["Categoria"] == cat_sel]["Equipamento"].tolist() if not df_maq.empty else []
                mod_sel = st.selectbox("Modelo da Máquina:", modelos_filtrados if modelos_filtrados else ["Nenhuma máquina nesta categoria"], key="mod_linha")
            
            if st.button("Adicionar Máquina à Composição"):
                if modelos_filtrados and mod_sel != "Nenhuma máquina nesta categoria":
                    preco_item = df_maq[df_maq["Equipamento"] == mod_sel]["Preco"].values[0]
                    st.session_state.carrinho.append({"Item": mod_sel, "Preco": float(preco_item), "Tipo": "Máquina"})
                    st.toast(f"{mod_sel} adicionado à linha!")
                    st.rerun()

        with st.expander("➕ Adicionar Periférico ou Kit Opcional"):
            lista_opcionais = df_kits["Equipamento"].tolist() if not df_kits.empty else []
            if lista_opcionais:
                kit_sel = st.selectbox("Selecione o Opcional:", lista_opcionais, key="kit_linha")
                if st.button("Adicionar Opcional à Composição"):
                    preco_kit = df_kits[df_kits["Equipamento"] == kit_sel]["Preco"].values[0]
                    st.session_state.carrinho.append({"Item": kit_sel, "Preco": float(preco_kit), "Tipo": "Kit"})
                    st.toast(f"{kit_sel} adicionado à linha!")
                    st.rerun()
            else:
                st.write("Nenhum periférico cadastrado na aba 'Kits'.")

        # --- LISTA DO ORÇAMENTO ATUAL ---
        st.markdown("### 📋 Composição da Linha Orçada")
        if not st.session_state.carrinho:
            st.info("Nenhum item adicionado à linha ainda.")
        else:
            itens_display = pd.DataFrame(st.session_state.carrinho)
            st.table(itens_display.assign(Preco=itens_display["Preco"].apply(formatar_real)))
            
            if st.button("🗑️ Limpar Toda a Linha"):
                st.session_state.carrinho = []
                st.rerun()
                
            st.markdown("---")
            
            # Caixa de seleção com os novos nomes de porte de empresa!
            segmento_sel = st.selectbox("Definir Porte da Empresa Cliente:", list(segmentos_opcoes.keys()))
            
            # Cálculos finais utilizando a porcentagem vinda da planilha
            subtotal_puro = sum(item["Preco"] for item in st.session_state.carrinho)
            porcentagem = segmentos_opcoes[segmento_sel]
            valor_segmento = subtotal_puro * porcentagem
            total_final = subtotal_puro + valor_segmento

            if modo_apresentacao:
                st.success(f"## **Valor Total da Linha: {formatar_real(total_final)}**")
                st.caption(f"Proposta comercial gerada para: {segmento_sel}.")
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("Subtotal Puro", formatar_real(subtotal_puro))
                c2.metric(f"Adicional Porte ({int(porcentagem*100)}%)", formatar_real(valor_segmento))
                c3.metric("Valor Sugerido Final", formatar_real(total_final))
