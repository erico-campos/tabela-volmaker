import streamlit as st
import pandas as pd

# Configuração da página para o celular
st.set_page_config(page_title="Volmaker - Sistema Comercial", page_icon="🏭", layout="centered")

# LINK DA SUA PLANILHA GOOGLE
LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/1W32LRAXpKWTL37-DeZiiSwBRnb0qYoY08slv767yw5o/edit"

def carregar_aba(nome_aba):
    try:
        # Transforma o link para o formato de exportação CSV apontando para a aba correta
        url_csv = LINK_PLANILHA.split("/edit")[0] + f"/gviz/tq?tqx=out:csv&sheet={nome_aba}"
        
        # Lê a aba tratando tudo inicialmente como texto
        df = pd.read_csv(url_csv, dtype=str)
        
        if not df.empty:
            # Remove colunas fantasmas sem nome
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            # Limpa espaços em branco nos nomes das colunas
            df.columns = df.columns.str.strip()
            # Limpa espaços em branco dentro das células
            for col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        return pd.DataFrame()

# --- CARREGAMENTO DAS ABAS ---
df_maq_raw = carregar_aba("Maquinas")
df_kits_raw = carregar_aba("Kits")
df_margens_raw = carregar_aba("Margens")

# --- FUNÇÃO AUXILIAR PARA LIMPAR PREÇOS ---
def limpar_preco(valor_str):
    if pd.isna(valor_str) or str(valor_str).lower() == 'nan' or str(valor_str).strip() == '':
        return 0.0
    limpo = str(valor_str).replace("R$", "").replace("r$", "").replace(" ", "")
    if "," in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    try:
        return float(limpo)
    except:
        return 0.0

# --- TRATAMENTO DA ABA "Maquinas" ---
if not df_maq_raw.empty and "Equipamento" in df_maq_raw.columns:
    df_maq = pd.DataFrame()
    df_maq["Categoria"] = df_maq_raw["Categoria"] if "Categoria" in df_maq_raw.columns else "Geral"
    df_maq["Equipamento"] = df_maq_raw["Equipamento"]
    df_maq["Preco"] = df_maq_raw["Preco"].apply(limpar_preco) if "Preco" in df_maq_raw.columns else 0.0
    df_maq = df_maq[df_maq["Equipamento"] != ""]
else:
    df_maq = pd.DataFrame(columns=["Categoria", "Equipamento", "Preco"])

# --- TRATAMENTO DA ABA "Kits" ---
if not df_kits_raw.empty and "Equipamento" in df_kits_raw.columns:
    df_kits = pd.DataFrame()
    df_kits["Equipamento"] = df_kits_raw["Equipamento"]
    df_kits["Preco"] = df_kits_raw["Preco"].apply(limpar_preco) if "Preco" in df_kits_raw.columns else 0.0
    df_kits = df_kits[df_kits["Equipamento"] != ""]
else:
    df_kits = pd.DataFrame(columns=["Equipamento", "Preco"])

# --- TRATAMENTO DA ABA "Margens" ---
segmentos_opcoes = {"Padrão de Fábrica (sem acrescentar porcentagem)": 0.0}
if not df_margens_raw.empty and "Porte" in df_margens_raw.columns:
    col_porcentagem = "Porcentagem" if "Porcentagem" in df_margens_raw.columns else df_margens_raw.columns[1]
    for _, linha in df_margens_raw.iterrows():
        porte_nome = str(linha["Porte"]).strip()
        if porte_nome and porte_nome.lower() != 'nan' and porte_nome != "":
            pct_str = str(linha[col_porcentagem]).replace("%", "").replace(",", ".")
            try:
                pct_val = float(pct_str) / 100
            except:
                pct_val = 0.0
            segmentos_opcoes[porte_nome] = pct_val
else:
    segmentos_opcoes = {
        "Padrão de Fábrica (sem acrescentar porcentagem)": 0.0,
        "Pequena Empresa": 0.0,
        "Media Empresa": 0.10,
        "Grande Empresa": 0.30,
        "Multinacional": 1.50
    }

categorias_comerciais = ["Envasadoras", "Tampadoras", "Ensacadeiras", "Detector de Furos", "Posicionadores e Elevadores", "Administrador de Peso", "Rotuladoras", "Robôs"]

# --- ESTADO DO CARRINHO DE COMPRAS ---
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

# --- PAINEL LATERAL ---
st.sidebar.header("⚙️ Configurações Comerciais")
modo_apresentacao = st.sidebar.toggle("👁️ Modo Apresentação (Esconder Interno)", value=False)

if not modo_apresentacao:
    st.sidebar.info("💡 Suas margens estão integradas à planilha!")
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Margens Carregadas")
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
        st.warning("Aguardando preenchimento ou ajuste de dados na planilha 'Maquinas'...")
    else:
        cat_filtro = st.selectbox("Filtrar por Categoria Comercial:", ["Todas"] + categorias_comerciais)
        df_mostrar = df_maq.copy() if cat_filtro == "Todas" else df_maq[df_maq["Categoria"] == cat_filtro].copy()
        
        if df_mostrar.empty:
            st.info(f"Nenhum equipamento localizado na categoria '{cat_filtro}'.")
        else:
            df_mostrar_formatado = df_mostrar.copy()
            df_mostrar_formatado["Preco"] = df_mostrar_formatado["Preco"].apply(formatar_real)
            st.dataframe(df_mostrar_formatado, use_container_width=True, hide_index=True)

# --- ABA 2: CONFIGURADOR DE LINHA ---
with aba_linha:
    if df_maq.empty:
        st.warning("Verifique os dados da planilha para liberar o configurador.")
    else:
        with st.expander("➕ Selecionar Máquina para a Linha", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                cat_sel = st.selectbox("Categoria da Máquina:", categorias_comerciais, key="cat_linha")
            with col2:
                modelos_filtrados = df_maq[df_maq["Categoria"] == cat_sel]["Equipamento"].tolist()
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
                st.write("Nenhum periférico localizado na aba 'Kits'.")

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
            
            segmento_sel = st.selectbox("Definir Porte da Empresa Cliente:", list(segmentos_opcoes.keys()))
            
            subtotal_puro = sum(item["Preco"] for item in st.session_state.carrinho)
            porcentagem = segmentos_opcoes[segmento_sel]
            valor_segmento = subtotal_puro * porcentagem
            total_final = subtotal_puro + valor_segmento

            if modo_apresentacao:
                st.success(f"## **Valor Total da Linha: {formatar_real(total_final)}**")
                st.caption(f"Proposta comercial gerada para o segmento: {segmento_sel}.")
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("Subtotal Puro", formatar_real(subtotal_puro))
                c2.metric(f"Adicional Porte ({int(porcentagem*100)}%)", formatar_real(valor_segmento))
                c3.metric("Valor Sugerido Final", formatar_real(total_final))
                
