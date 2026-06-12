import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página para o celular
st.set_page_config(page_title="Volmaker - Configurador de Linhas", page_icon="🏭", layout="centered")

# --- CONEXÃO COM O GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Tentar ler dados da aba Maquinas
    try:
        df_maq = conn.read(worksheet="Maquinas", ttl=5)
        if df_maq.empty or "Categoria" not in df_maq.columns:
            df_maq = pd.DataFrame(columns=["Categoria", "Equipamento", "Preco"])
    except:
        df_maq = pd.DataFrame(columns=["Categoria", "Equipamento", "Preco"])
        
    # Tentar ler dados da aba Kits
    try:
        df_kits = conn.read(worksheet="Kits", ttl=5)
        if df_kits.empty or "Equipamento" not in df_kits.columns:
            df_kits = pd.DataFrame(columns=["Equipamento", "Preco"])
    except:
        df_kits = pd.DataFrame(columns=["Equipamento", "Preco"])
except Exception as e:
    st.error(f"Erro na conexão com o banco de dados. Verifique os Secrets. Erro: {e}")
    st.stop()

# --- DADOS PADRÃO (Caso a planilha esteja zerada no primeiro uso) ---
if df_maq.empty:
    dados_padrao_maq = {
        "Categoria": ["Envasadoras", "Envasadoras", "Envasadoras", "Envasadoras", "Envasadoras", "Envasadoras", "Envasadoras", "Envasadoras", "Tampadoras", "Tampadoras", "Tampadoras", "Tampadoras", "Tampadoras", "Ensacadeiras", "Ensacadeiras", "Ensacadeiras", "Ensacadeiras", "Detector de Furos", "Detector de Furos", "Posicionadores e Elevadores", "Posicionadores e Elevadores", "Posicionadores e Elevadores", "Posicionadores e Elevadores", "Posicionadores e Elevadores", "Posicionadores e Elevadores", "Posicionadores e Elevadores", "Administrador de Peso"],
        "Equipamento": ["ENVASADORA POR CELULA DE CARGA 4 BICOS 5L (PPZ)", "ENVASADORA POR CELULA DE CARGA 4 BICOS 20L (PPZ)", "ENVASADORA POR CELULA DE CARGA 4 BICOS 5L (INOX)", "ENVASADORA POR CELULA DE CARGA 4 BICOS 20L (INOX)", "ENVASADORA LINEAR GRAVIMÉTRICA (PPZ)", "ENVASADORA LINEAR GRAVIMÉTRICA (INOX)", "ENVASADORA LINEAR VOLUMÉTRICA 10 BICOS (INOX)", "ENVASADORA ROTATIVA CÉLULA DE CARGA MONOBLOCO 16/8", "TAMPADORA DE BALDES SLIM", "TAMPADORA DE BALDES COM ALIMENTAÇÃO AUTOMÁTICA DE TAMPAS", "TAMPADORA TANGENCIAL", "TAMPADORA PASSO A PASSO SEM ALIMENTADOR DE TAMPAS", "TAMPADORA LINEAR", "ENSACADEIRA AMPLA C/ SOLDA", "ENSACADEIRA AMPLA S/ SOLDA", "ENSACADEIRA SLIM C/SOLDA", "ENSACADEIRA SLIM S/ SOLDA", "DETECTOR DE FUROS MODELO GOLD", "DETECTOR DE FUROS MODELO SLIM", "POSICIONADOR DE FRASCOS PADRÃO", "POSICIONADOR DE FRASCOS COMPACTO", "POSICIONADOR DE FRASCOS MINI", "ELEVADOR DE FRASCOS COM SILO", "CARREGADOR DE PREFORMA MOD. SC-001", "ELEVADOR DE TAMPAS", "ELEVADOR SELECIONADOR DE TAMPAS", "ADMINISTRADOR DE PESO"],
        "Preco": [131450.00, 157635.00, 131450.00, 157635.00, 193310.00, 193310.00, 317121.00, 1060250.00, 121159.00, 213600.00, 127422.00, 151810.00, 77550.00, 172146.00, 137122.00, 146333.00, 119218.00, 71633.00, 53396.00, 147239.00, 137111.00, 109213.00, 73202.00, 77190.00, 37412.00, 93141.00, 189500.00]
    }
    df_maq = pd.DataFrame(dados_padrao_maq)
    conn.update(worksheet="Maquinas", data=df_maq)

if df_kits.empty:
    dados_padrao_kits = {
        "Equipamento": ["PENTE DA ENVASADORA 12 BICOS", "BICO DE AÇO INOXIDÁVEL ATÉ PCO 28MM", "BICO DE AÇO INOXIDÁVEL ACIMA DE PCO 28MM"],
        "Preco": [10320.00, 1452.00, 1742.40]
    }
    df_kits = pd.DataFrame(dados_padrao_kits)
    conn.update(worksheet="Kits", data=df_kits)

# Lista fixa de categorias para organização
categorias_comerciais = ["Envasadoras", "Tampadoras", "Ensacadeiras", "Detector de Furos", "Posicionadores e Elevadores", "Administrador de Peso", "Rotuladoras", "Robôs"]

# --- ESTADO DA SESSÃO (CARRINHO DE COMPRAS) ---
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

# --- PAINEL LATERAL ---
st.sidebar.header("⚙️ Configurações Técnicas")
modo_apresentacao = st.sidebar.toggle("👁️ Modo Apresentação (Esconder Interno)", value=False)

if not modo_apresentacao:
    modo_sistema = st.sidebar.radio("Ir para:", ["Montar Linha Completa", "Gerenciar Banco de Dados"])
    st.sidebar.markdown("---")
    st.sidebar.subheader("Porcentagens por Segmento")
    m_limp = st.sidebar.number_input("Produtos de Limpeza (%)", value=0.0, step=1.0)
    m_alim = st.sidebar.number_input("Alimentício (%)", value=10.0, step=1.0)
    m_cosm = st.sidebar.number_input("Cosméticos (%)", value=15.0, step=1.0)
    m_pharma = st.sidebar.number_input("Farmacêutico (%)", value=30.0, step=1.0)
else:
    modo_sistema = "Montar Linha Completa"
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

# --- MÓDULO 1: SIMULADOR DE LINHA COMPLETA ---
if modo_sistema == "Montar Linha Completa":
    st.title("🏭 Configurador de Linha de Produção")
    
    with st.expander("➕ Adicionar Equipamento à Linha", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            cat_sel = st.selectbox("Categoria:", categorias_comerciais)
        with col2:
            modelos_filtrados = df_maq[df_maq["Categoria"] == cat_sel]["Equipamento"].tolist()
            mod_sel = st.selectbox("Modelo:", modelos_filtrados if modelos_filtrados else ["Nenhum cadastrado"])
        
        if st.button("Adicionar este Item à Linha"):
            if modelos_filtrados:
                preco_item = df_maq[df_maq["Equipamento"] == mod_sel]["Preco"].values[0]
                st.session_state.carrinho.append({"Item": mod_sel, "Preco": float(preco_item), "Tipo": "Máquina"})
                st.toast(f"{mod_sel} adicionado!")
                st.rerun()

    with st.expander("➕ Adicionar Periférico / Kit Opcional"):
        kit_sel = st.selectbox("Selecione o Opcional:", df_kits["Equipamento"].tolist())
        if st.button("Adicionar Opcional à Linha"):
            preco_kit = df_kits[df_kits["Equipamento"] == kit_sel]["Preco"].values[0]
            st.session_state.carrinho.append({"Item": kit_sel, "Preco": float(preco_kit), "Tipo": "Kit"})
            st.toast(f"{kit_sel} adicionado!")
            st.rerun()

    # --- EXIBIÇÃO DA LINHA MONTADA ---
    st.markdown("### 📋 Itens da Proposta")
    if not st.session_state.carrinho:
        st.info("Sua linha está vazia. Adicione equipamentos acima.")
    else:
        # Tabela de itens no carrinho
        itens_display = pd.DataFrame(st.session_state.carrinho)
        st.table(itens_display.assign(Preco=itens_display["Preco"].apply(formatar_real)))
        
        if st.button("🗑️ Limpar Orçamento"):
            st.session_state.carrinho = []
            st.rerun()
            
        st.markdown("---")
        segmento_sel = st.selectbox("Configuração Técnica de Segmento:", list(segmentos_opcoes.keys()))
        
        # Cálculos Finais
        subtotal_puro = sum(item["Preco"] for item in st.session_state.carrinho)
        porcentagem = segmentos_opcoes[segmento_sel]
        valor_segmento = subtotal_puro * porcentagem
        total_final = subtotal_puro + valor_segmento

        if modo_apresentacao:
            st.success(f"## **Valor Total da Linha: {formatar_real(total_final)}**")
            st.caption(f"Configuração para o segmento {segmento_sel}.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Subtotal Itens", formatar_real(subtotal_puro))
            c2.metric(f"Ajuste Segmento ({int(porcentagem*100)}%)", formatar_real(valor_segmento))
            c3.metric("Total Final", formatar_real(total_final))
            st.success(f"### Preço Sugerido: {formatar_real(total_final)}")

# --- MÓDULO 2: GERENCIADOR DE BANCO DE DADOS ---
else:
    st.title("🛠️ Gerenciador de Preços (Google Sheets)")
    st.write("Edite aqui para salvar permanentemente na sua Planilha Google.")
    
    aba1, aba2 = st.tabs(["Máquinas", "Periféricos/Kits"])
    
    with aba1:
        cat_m = st.selectbox("Selecione Categoria para Editar/Adicionar:", categorias_comerciais)
        acao = st.radio("Ação:", ["Adicionar Novo", "Editar Preço", "Excluir"], horizontal=True)
        
        if acao == "Adicionar Novo":
            n_nome = st.text_input("Nome da Máquina:").strip().upper()
            n_preco = st.number_input("Preço Fábrica:", min_value=0.0, step=100.0)
            if st.button("Salvar Nova Máquina"):
                nova_linha = pd.DataFrame([{"Categoria": cat_m, "Equipamento": n_nome, "Preco": n_preco}])
                df_maq = pd.concat([df_maq, nova_linha], ignore_index=True)
                conn.update(worksheet="Maquinas", data=df_maq)
                st.success("Salvo com sucesso!")
                st.rerun()
        
        elif acao == "Editar Preço":
            maquinas_cat = df_maq[df_maq["Categoria"] == cat_m]["Equipamento"].tolist()
            if maquinas_cat:
                m_sel = st.selectbox("Equipamento:", maquinas_cat)
                p_atual = df_maq[df_maq["Equipamento"] == m_sel]["Preco"].values[0]
                n_p = st.number_input("Novo Preço:", value=float(p_atual), step=100.0)
                if st.button("Atualizar Preço"):
                    df_maq.loc[df_maq["Equipamento"] == m_sel, "Preco"] = n_p
                    conn.update(worksheet="Maquinas", data=df_maq)
                    st.success("Preço atualizado!")
                    st.rerun()

        elif acao == "Excluir":
            maquinas_cat = df_maq[df_maq["Categoria"] == cat_m]["Equipamento"].tolist()
            if maquinas_cat:
                m_del = st.selectbox("Equipamento para excluir:", maquinas_cat)
                if st.button("Confirmar Exclusão"):
                    df_maq = df_maq[df_maq["Equipamento"] != m_del]
                    conn.update(worksheet="Maquinas", data=df_maq)
                    st.warning("Excluído!")
                    st.rerun()

    with aba2:
        st.write("#### Gerenciar Periféricos")
        acao_k = st.radio("Ação Kit:", ["Adicionar Kit", "Editar Kit", "Excluir Kit"], horizontal=True)
        
        if acao_k == "Adicionar Kit":
            nk_nome = st.text_input("Nome do Periférico:").strip().upper()
            nk_preco = st.number_input("Preço Kit:", min_value=0.0, step=50.0)
            if st.button("Salvar Novo Kit"):
                nk_lin = pd.DataFrame([{"Equipamento": nk_nome, "Preco": nk_preco}])
                df_kits = pd.concat([df_kits, nk_lin], ignore_index=True)
                conn.update(worksheet="Kits", data=df_kits)
                st.success("Kit salvo!")
                st.rerun()
        
        elif acao_k == "Editar Kit":
            k_sel = st.selectbox("Selecionar Kit:", df_kits["Equipamento"].tolist())
            pk_at = df_kits[df_kits["Equipamento"] == k_sel]["Preco"].values[0]
            nk_p = st.number_input("Novo Preço Kit:", value=float(pk_at), step=50.0)
            if st.button("Atualizar Kit"):
                df_kits.loc[df_kits["Equipamento"] == k_sel, "Preco"] = nk_p
                conn.update(worksheet="Kits", data=df_kits)
                st.success("Kit atualizado!")
                st.rerun()

        elif acao_k == "Excluir Kit":
            k_del = st.selectbox("Kit para deletar:", df_kits["Equipamento"].tolist())
            if st.button("Confirmar Exclusão Kit"):
                df_kits = df_kits[df_kits["Equipamento"] != k_del]
                conn.update(worksheet="Kits", data=df_kits)
                st.warning("Kit removido!")
                st.rerun()



