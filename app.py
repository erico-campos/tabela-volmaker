import streamlit as st
import pandas as pd

# Configuração da página para o celular
st.set_page_config(page_title="Volmaker - Sistema Comercial", page_icon="🏭", layout="centered")

# COLE O SEU LINK DA WEB AQUI DENTRO DAS ASPAS (Substitua este exemplo abaixo pelo seu)
LINK_PUBLICADO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRglKoykw-0_YzOIyUDL_L_QRsW9Ga7S8ZjWg-TuLrsCmZUkB1wIbcTsocaWrwvyTlG3D5gnyoyBuPv/pub?output=csv"


def carregar_dados_blindado(link_base, nome_aba):
    try:
        # Transforma o link de publicação para o formato CSV focado na aba solicitada
        if "pub?" in link_base:
            url_limpa = link_base.split("pub?")[0]
            url = f"{url_limpa}pub?output=csv&sheet={nome_aba}"
        else:
            ID = "1W32LRAXpKWTL37-DeZiiSwBRnb0qYoY08slv767yw5o"
            url = f"https://docs.google.com/spreadsheets/d/{ID}/export?format=csv&sheet={nome_aba}"

        df = pd.read_csv(url, dtype=str, encoding='utf-8')

        if not df.empty:
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            df.columns = df.columns.str.strip()
            for col in df.columns:
                df[col] = df[col].astype(str).str.strip()
            return df
        return pd.DataFrame()
    except:
        # Contingência total usando os GIDs fixos caso o mapeamento por nome falhe
        try:
            gids = {"Maquinas": "0", "Margens": "1061587479", "Kits": "1114006122"}
            gid = gids.get(nome_aba, "0")
            ID_RESERVA = "1W32LRAXpKWTL37-DeZiiSwBRnb0qYoY08slv767yw5o"
            url_fallback = f"https://docs.google.com/spreadsheets/d/{ID_RESERVA}/export?format=csv&gid={gid}"
            df = pd.read_csv(url_fallback, dtype=str, encoding='utf-8')
            df.columns = df.columns.str.strip()
            return df
        except:
            return pd.DataFrame()


# Carregando as abas de forma protegida
df_maq_raw = carregar_dados_blindado(LINK_PUBLICADO, "Maquinas")
df_kits_raw = carregar_dados_blindado(LINK_PUBLICADO, "Kits")
df_margens_raw = carregar_dados_blindado(LINK_PUBLICADO, "Margens")


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


# --- TRATAMENTO MÁQUINAS ---
if not df_maq_raw.empty:
    df_maq = pd.DataFrame()
    col_cat = "Categoria" if "Categoria" in df_maq_raw.columns else df_maq_raw.columns[0]
    col_equip = "Equipamento" if "Equipamento" in df_maq_raw.columns else df_maq_raw.columns[1]
    col_preco = ""
    for c in df_maq_raw.columns:
        if "prec" in c.lower(): col_preco = c
    if not col_preco: col_preco = df_maq_raw.columns[2] if len(df_maq_raw.columns) > 2 else df_maq_raw.columns[-1]

    df_maq["Categoria"] = df_maq_raw[col_cat].astype(str).str.strip()
    df_maq["Equipamento"] = df_maq_raw[col_equip].astype(str).str.strip()
    df_maq["Preco"] = df_maq_raw[col_preco].apply(limpar_preco)
    df_maq = df_maq[df_maq["Equipamento"] != ""]
else:
    df_maq = pd.DataFrame(columns=["Categoria", "Equipamento", "Preco"])

# --- TRATAMENTO KITS ---
if not df_kits_raw.empty:
    df_kits = pd.DataFrame()
    col_equip_k = "Equipamento" if "Equipamento" in df_kits_raw.columns else df_kits_raw.columns[0]
    col_preco_k = ""
    for c in df_kits_raw.columns:
        if "prec" in c.lower(): col_preco_k = c
    if not col_preco_k: col_preco_k = df_kits_raw.columns[1] if len(df_kits_raw.columns) > 1 else df_kits_raw.columns[
        -1]

    df_kits["Equipamento"] = df_kits_raw[col_equip_k].astype(str).str.strip()
    df_kits["Preco"] = df_kits_raw[col_preco_k].apply(limpar_preco)
    df_kits = df_kits[df_kits["Equipamento"] != ""]
else:
    df_kits = pd.DataFrame(columns=["Equipamento", "Preco"])

# --- TRATAMENTO MARGENS ---
segmentos_opcoes = {"Padrão de Fábrica (sem acrescentar porcentagem)": 0.0}
if not df_margens_raw.empty:
    col_porte = "Porte" if "Porte" in df_margens_raw.columns else df_margens_raw.columns[0]
    col_pct = "Porcentagem" if "Porcentagem" in df_margens_raw.columns else df_margens_raw.columns[1]
    for _, linha in df_margens_raw.iterrows():
        porte_nome = str(linha[col_porte]).strip()
        if porte_nome and porte_nome.lower() != 'nan' and porte_nome != "":
            pct_str = str(linha[col_pct]).replace("%", "").replace(",", ".")
            try:
                pct_val = float(pct_str) / 100
            except:
                pct_val = 0.0
            segmentos_opcoes[porte_nome] = pct_val

categorias_comerciais = ["Envasadoras", "Tampadoras", "Ensacadeiras", "Detector de Furos",
                         "Posicionadores e Elevadores", "Administrador de Peso", "Rotuladoras", "Robôs"]

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

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


st.title("🏭 Orçador Inteligente - Volmaker")
aba_tabela, aba_linha = st.tabs(["🔍 Ver Tabela de Preços", "🛒 Montar Linha Completa"])

with aba_tabela:
    st.markdown("### Lista Geral de Equipamentos Cadastrados")
    if df_maq.empty:
        st.error("Aguardando ativação do link de publicação na web...")
    else:
        cat_filtro = st.selectbox("Filtrar por Categoria Comercial:", ["Todas"] + categorias_comerciais)
        df_mostrar = df_maq.copy() if cat_filtro == "Todas" else df_maq[df_maq["Categoria"] == cat_filtro].copy()

        if df_mostrar.empty:
            st.info(f"Nenhum equipamento localizado na categoria '{cat_filtro}'.")
        else:
            df_mostrar_formatado = df_mostrar.copy()
            df_mostrar_formatado["Preco"] = df_mostrar_formatado["Preco"].apply(formatar_real)
            st.dataframe(df_mostrar_formatado, use_container_width=True, hide_index=True)

with aba_linha:
    if df_maq.empty:
        st.warning("Aguardando sincronização dos dados...")
    else:
        with st.expander("➕ Selecionar Máquina para a Linha", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                cat_sel = st.selectbox("Categoria da Máquina:", categorias_comerciais, key="cat_linha")
            with col2:
                modelos_filtrados = df_maq[df_maq["Categoria"] == cat_sel]["Equipamento"].tolist()
                mod_sel = st.selectbox("Modelo da Máquina:",
                                       modelos_filtrados if modelos_filtrados else ["Nenhuma máquina nesta categoria"],
                                       key="mod_linha")
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
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("Subtotal Puro", formatar_real(subtotal_puro))
                c2.metric(f"Adicional Porte ({int(porcentagem * 100)}%)", formatar_real(valor_segmento))
                c3.metric("Valor Sugerido Final", formatar_real(total_final))
