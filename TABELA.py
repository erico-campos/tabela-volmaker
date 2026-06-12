import streamlit as st
import json
import os

# Configuração da página para o celular
st.set_page_config(page_title="Orçador Comercial V5", page_icon="🏭", layout="centered")

ARQUIVO_BANCO = "banco_precos.json"

# Dados iniciais padrão de fábrica
dados_iniciais_categorias = {
    "Envasadoras": {
        "ENVASADORA POR CELULA DE CARGA 4 BICOS 5L (PPZ)": 131450.00,
        "ENVASADORA POR CELULA DE CARGA 4 BICOS 20L (PPZ)": 157635.00,
        "ENVASADORA POR CELULA DE CARGA 4 BICOS 5L (INOX)": 131450.00,
        "ENVASADORA POR CELULA DE CARGA 4 BICOS 20L (INOX)": 157635.00,
        "ENVASADORA LINEAR GRAVIMÉTRICA (PPZ)": 193310.00,
        "ENVASADORA LINEAR GRAVIMÉTRICA (INOX)": 193310.00,
        "ENVASADORA LINEAR VOLUMÉTRICA 10 BICOS (INOX)": 317121.00,
        "ENVASADORA ROTATIVA CÉLULA DE CARGA MONOBLOCO 16/8": 1060250.00,
    },
    "Tampadoras": {
        "TAMPADORA DE BALDES SLIM": 121159.00,
        "TAMPADORA DE BALDES COM ALIMENTAÇÃO AUTOMÁTICA DE TAMPAS": 213600.00,
        "TAMPADORA TANGENCIAL": 127422.00,
        "TAMPADORA PASSO A PASSO SEM ALIMENTADOR DE TAMPAS": 151810.00,
        "TAMPADORA LINEAR": 77550.00,
    },
    "Ensacadeiras": {
        "ENSACADEIRA AMPLA C/ SOLDA": 172146.00,
        "ENSACADEIRA AMPLA S/ SOLDA": 137122.00,
        "ENSACADEIRA SLIM C/SOLDA": 146333.00,
        "ENSACADEIRA SLIM S/ SOLDA": 119218.00,
    },
    "Detector de Furos": {
        "DETECTOR DE FUROS MODELO GOLD": 71633.00,
        "DETECTOR DE FUROS MODELO SLIM": 53396.00,
    },
    "Posicionadores e Elevadores": {
        "POSICIONADOR DE FRASCOS PADRÃO": 147239.00,
        "POSICIONADOR DE FRASCOS COMPACTO": 137111.00,
        "POSICIONADOR DE FRASCOS MINI": 109213.00,
        "ELEVADOR DE FRASCOS COM SILO": 73202.00,
        "CARREGADOR DE PREFORMA MOD. SC-001": 77190.00,
        "ELEVADOR DE TAMPAS": 37412.00,
        "ELEVADOR SELECIONADOR DE TAMPAS": 93141.00,
    },
    "Administrador de Peso": {
        "ADMINISTRADOR DE PESO": 189500.00,
    },
    "Rotuladoras": {},
    "Robôs": {}
}

dados_iniciais_kits = {
    "PENTE DA ENVASADORA 12 BICOS": 10320.00,
    "BICO DE AÇO INOXIDÁVEL ATÉ PCO 28MM": 1452.00,
    "BICO DE AÇO INOXIDÁVEL ACIMA DE PCO 28MM": 1742.40,
}


def carregar_dados():
    if not os.path.exists(ARQUIVO_BANCO):
        banco_completo = {"maquinas": dados_iniciais_categorias, "kits": dados_iniciais_kits}
        with open(ARQUIVO_BANCO, 'w', encoding='utf-8') as f:
            json.dump(banco_completo, f, ensure_ascii=False, indent=4)
        return banco_completo
    else:
        with open(ARQUIVO_BANCO, 'r', encoding='utf-8') as f:
            return json.load(f)


def salvar_dados(dados):
    with open(ARQUIVO_BANCO, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


banco = carregar_dados()
dados_categorias = banco["maquinas"]
dados_kits = banco["kits"]

# --- PAINEL DE CONTROLE LATERAL ---
st.sidebar.header("⚙️ Configurações Internas")
modo_apresentacao = st.sidebar.toggle("👁️ Modo Apresentação (Esconder Margens)", value=False)

if not modo_apresentacao:
    modo_sistema = st.sidebar.radio("Navegar para:", ["Simulador de Vendas", "Gerenciar Banco de Dados"])
    st.sidebar.markdown("---")
    st.sidebar.subheader("Porcentagens por Segmento")
    if 'm_pharma' not in st.session_state: st.session_state.m_pharma = 30.0
    if 'm_cosm' not in st.session_state: st.session_state.m_cosm = 15.0
    if 'm_alim' not in st.session_state: st.session_state.m_alim = 10.0
    if 'm_limp' not in st.session_state: st.session_state.m_limp = 0.0

    st.session_state.m_pharma = st.sidebar.number_input("Farmacêutico (%)", value=st.session_state.m_pharma, step=1.0)
    st.session_state.m_cosm = st.sidebar.number_input("Cosméticos (%)", value=st.session_state.m_cosm, step=1.0)
    st.session_state.m_alim = st.sidebar.number_input("Alimentício (%)", value=st.session_state.m_alim, step=1.0)
    st.session_state.m_limp = st.sidebar.number_input("Produtos de Limpeza (%)", value=st.session_state.m_limp,
                                                      step=1.0)
else:
    modo_sistema = "Simulador de Vendas"
    st.sidebar.warning("🔒 Modo Apresentação ativo.")

segmentos_opcoes = {
    "Padrão de Fábrica": 0.0,
    "Produtos de Limpeza": st.session_state.get('m_limp', 0.0) / 100,
    "Alimentício": st.session_state.get('m_alim', 10.0) / 100,
    "Cosméticos": st.session_state.get('m_cosm', 15.0) / 100,
    "Farmacêutico": st.session_state.get('m_pharma', 30.0) / 100
}


def formatar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")


# --- MÓDULO 1: SIMULADOR DE VENDAS ---
if modo_sistema == "Simulador de Vendas":
    st.title("🏭 Proposta Técnica de Equipamentos")
    categorias_validas = [cat for cat, itens in dados_categorias.items() if itens]

    if not categorias_validas:
        st.warning("⚠️ Banco de dados sem itens cadastrados.")
    else:
        categoria_selecionada = st.selectbox("Selecione a Categoria do Equipamento:", categorias_validas)
        modelo_selecionado = st.selectbox("Selecione o Modelo da Máquina:",
                                          list(dados_categorias[categoria_selecionada].keys()))
        preco_maquina = dados_categorias[categoria_selecionada][modelo_selecionado]

        kits_selecionados = st.multiselect("Deseja incluir Periféricos / Acessórios Opcionais?",
                                           list(dados_kits.keys()))
        preco_kits = sum([dados_kits[kit] for kit in kits_selecionados])

        segmento_selecionado = st.selectbox("Configuração Técnica da Linha:", list(segmentos_opcoes.keys()))

        preco_base_total = preco_maquina + preco_kits
        porcentagem_segmento = segmentos_opcoes[segmento_selecionado]
        valor_acrescimo_segmento = preco_base_total * porcentagem_segmento
        preco_final_proposta = preco_base_total + valor_acrescimo_segmento

        st.markdown("---")
        if modo_apresentacao:
            st.subheader("📋 Resumo da Configuração Solicitada")
            st.markdown(f"**Equipamento Principal:** {modelo_selecionado}")
            if kits_selecionados:
                st.markdown("**Acessórios Incluídos:**")
                for kit in kits_selecionados:
                    st.markdown(f"- *{kit}*")
            st.markdown(" ")
            st.success(f"### **Preço Final de Fornecimento: {formatar_real(preco_final_proposta)}**")
            st.caption("Preço sob condições padrão de tabela. Válido para a configuração técnica selecionada acima.")
        else:
            st.subheader("🕵️ Visão Interna do Consultor (SÓ VOCÊ VÊ)")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Preço Base Máquina", value=formatar_real(preco_maquina))
                st.metric(label="Total em Periféricos", value=formatar_real(preco_kits))
            with col2:
                st.metric(label="Subtotal Puro", value=formatar_real(preco_base_total))
                st.metric(label=f"Acréscimo Comercial ({int(porcentagem_segmento * 100)}%)",
                          value=formatar_real(valor_acrescimo_segmento))
            st.success(f"## **Preço Final: {formatar_real(preco_final_proposta)}**")

# --- MÓDULO 2: GERENCIADOR DO BANCO DE DADOS (COM EDIÇÃO INTEGRADA) ---
else:
    st.markdown("### 🛠️ Gerenciador de Itens e Catálogo")
    st.write("Crie novos itens ou selecione um existente para alterar o valor.")

    aba_maquina, aba_kits = st.tabs(["Maquinas e Modelos", "Periféricos e Opcionais"])

    with aba_maquina:
        st.write("#### 📝 Adicionar ou Editar Equipamento")
        cat_edit = st.selectbox("Escolha a Categoria Comercial:", list(dados_categorias.keys()))

        # Sistema Inteligente de Seleção para Edição
        acao_maq = st.radio("O que deseja fazer?", ["Adicionar Novo Modelo", "Editar Preço de Modelo Existente"],
                            horizontal=True)

        if acao_maq == "Editar Preço de Modelo Existente":
            if dados_categorias[cat_edit]:
                modelo_para_editar = st.selectbox("Selecione a máquina que deseja alterar:",
                                                  list(dados_categorias[cat_edit].keys()))
                preco_atual = dados_categorias[cat_edit][modelo_para_editar]
                st.info(f"Preço atual registrado: {formatar_real(preco_atual)}")

                # O input já vem preenchido com o valor antigo para você só ajustar
                novo_preco = st.number_input("Digite o Novo Preço (R$):", value=float(preco_atual), min_value=0.0,
                                             step=100.0, key="edit_maq_val")

                if st.button("💾 Atualizar Preço da Máquina"):
                    dados_categorias[cat_edit][modelo_para_editar] = novo_preco
                    banco["maquinas"] = dados_categorias
                    salvar_dados(banco)
                    st.success(f"Preço de {modelo_para_editar} atualizado com sucesso!")
                    st.rerun()
            else:
                st.warning("Não há máquinas cadastradas nesta categoria para editar.")

        else:  # Adicionar Novo
            nome_modelo = st.text_input("Nome da Nova Máquina/Modelo:").strip().upper()
            preco_modelo = st.number_input("Preço de Tabela Base (R$):", min_value=0.0, step=100.0, key="new_maq_val")

            if st.button("➕ Cadastrar Nova Máquina"):
                if nome_modelo:
                    dados_categorias[cat_edit][nome_modelo] = preco_modelo
                    banco["maquinas"] = dados_categorias
                    salvar_dados(banco)
                    st.success(f"{nome_modelo} adicionada ao catálogo!")
                    st.rerun()
                else:
                    st.error("Insira o nome do modelo.")

        st.markdown("---")
        st.write("#### 🗑️ Excluir Equipamento do Sistema")
        cat_del = st.selectbox("Categoria para exclusão:", list(dados_categorias.keys()), key="cat_del_maq")
        if dados_categorias[cat_del]:
            modelo_del = st.selectbox("Escolha o modelo para deletar definitivamente:",
                                      list(dados_categorias[cat_del].keys()))
            if st.button("❌ Deletar Modelo", type="primary", key="btn_del_maq"):
                del dados_categorias[cat_del][modelo_del]
                banco["maquinas"] = dados_categorias
                salvar_dados(banco)
                st.warning(f"O modelo {modelo_del} foi removido.")
                st.rerun()

    with aba_kits:
        st.write("#### 📝 Adicionar ou Editar Periférico / Opcional")

        acao_kit = st.radio("O que deseja fazer?",
                            ["Adicionar Novo Periférico", "Editar Preço de Periférico Existente"], horizontal=True)

        if acao_kit == "Editar Preço de Periférico Existente":
            if dados_kits:
                kit_para_editar = st.selectbox("Selecione o periférico que deseja alterar:", list(dados_kits.keys()))
                preco_kit_atual = dados_kits[kit_para_editar]
                st.info(f"Preço atual registrado: {formatar_real(preco_kit_atual)}")

                novo_preco_kit = st.number_input("Digite o Novo Preço do Periférico (R$):",
                                                 value=float(preco_kit_atual), min_value=0.0, step=50.0,
                                                 key="edit_kit_val")

                if st.button("💾 Atualizar Preço do Periférico"):
                    dados_kits[kit_para_editar] = novo_preco_kit
                    banco["kits"] = dados_kits
                    salvar_dados(banco)
                    st.success(f"Preço de {kit_para_editar} atualizado com sucesso!")
                    st.rerun()
            else:
                st.warning("Não há periféricos cadastrados para editar.")

        else:  # Adicionar Novo Periférico
            nome_kit = st.text_input("Nome do Novo Periférico / Acessório:").strip().upper()
            preco_kit = st.number_input("Preço de Tabela do Periférico (R$):", min_value=0.0, step=50.0,
                                        key="new_kit_val")

            if st.button("➕ Cadastrar Novo Periférico"):
                if nome_kit:
                    dados_kits[nome_kit] = preco_kit
                    banco["kits"] = dados_kits
                    salvar_dados(banco)
                    st.success(f"Periférico '{nome_kit}' adicionado ao catálogo!")
                    st.rerun()
                else:
                    st.error("Insira o nome do periférico.")

        st.markdown("---")
        st.write("#### 🗑️ Excluir Periférico do Sistema")
        if dados_kits:
            kit_del = st.selectbox("Escolha o periférico para deletar definitivamente:", list(dados_kits.keys()))
            if st.button("❌ Deletar Periférico", type="primary", key="btn_del_kit"):
                del dados_kits[kit_del]
                banco["kits"] = dados_kits
                salvar_dados(banco)
                st.warning(f"O periférico {kit_del} foi removido.")
                st.rerun()
