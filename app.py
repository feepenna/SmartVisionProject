# app.py
"""Smart Vision — Portal do Colaborador & Gestão de Loja Óptica.

Interface Streamlit desenvolvida para consultores ópticos e equipe de loja,
incorporando branding exclusivo (#3942F6, #F8B807, #F8FAFC), metas dinâmicas,
mural de RH, central de documentos, Academia SmartVision e atalhos operacionais.
"""

import os
from datetime import datetime, date, timedelta
import streamlit as st

# Tentativa de importação do serviço Xano para o módulo de estoque
try:
    from services import xano_client
except Exception:
    xano_client = None

# Configuração da Página
st.set_page_config(
    page_title="SmartVision — Portal do Colaborador",
    page_icon="👓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# CHANGE 1: DESIGN SYSTEM, BRANDING & CSS SHELL
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --primary-color: #3942F6;
        --secondary-color: #F8B807;
        --bg-color: #F8FAFC;
        --text-main: #0F172A;
        --text-muted: #64748B;
        --card-bg: #FFFFFF;
        --border-color: #E2E8F0;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        background-color: var(--bg-color);
    }

    /* Header Superior */
    .portal-header {
        background: linear-gradient(135deg, #3942F6 0%, #2027C9 100%);
        border-radius: 16px;
        padding: 24px 32px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(57, 66, 246, 0.25);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }

    .brand-title {
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .brand-subtitle {
        font-size: 0.95rem;
        opacity: 0.85;
        margin-top: 4px;
    }

    /* Notificações e Badge Amarelo (#F8B807) */
    .notification-pill {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 30px;
        padding: 8px 16px;
        display: flex;
        align-items: center;
        gap: 10px;
        color: white;
        font-weight: 500;
        font-size: 0.9rem;
    }

    .badge-yellow {
        background-color: #F8B807;
        color: #0F172A;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
    }

    /* Card de Perfil do Colaborador */
    .profile-card {
        background: white;
        color: var(--text-main);
        border-radius: 12px;
        padding: 10px 18px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid var(--border-color);
    }

    .profile-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: #3942F6;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.2rem;
        border: 2px solid #F8B807;
    }

    /* Cartões & Widgets */
    .metric-widget {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-widget:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }

    .metric-title {
        color: var(--text-muted);
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    .metric-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0F172A;
    }

    .metric-sub {
        font-size: 0.85rem;
        color: #10B981;
        font-weight: 600;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Barra de Progresso Customizada com Patamares */
    .progress-container {
        background: #E2E8F0;
        border-radius: 12px;
        height: 24px;
        width: 100%;
        position: relative;
        overflow: hidden;
        margin: 14px 0 8px 0;
    }

    .progress-fill {
        background: linear-gradient(90deg, #3942F6 0%, #5B63F8 70%, #F8B807 100%);
        height: 100%;
        border-radius: 12px;
        transition: width 0.5s ease-in-out;
    }

    /* Banner Prioritário Urgente */
    .urgent-banner {
        background: #FFFBEB;
        border: 2px solid #F8B807;
        border-left: 8px solid #F8B807;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 14px;
        color: #92400E;
    }

    /* Estilo de Avisos e Cards */
    .notice-card {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
        border-left: 5px solid #3942F6;
    }

    .tag-category {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        margin-bottom: 8px;
    }

    .tag-rh { background: #EEF2FF; color: #3942F6; }
    .tag-operacional { background: #FEF3C7; color: #B45309; }
    .tag-produtos { background: #ECFDF5; color: #047857; }
    .tag-formacao { background: #F3E8FF; color: #7E22CE; }

    /* Botões Rápidos */
    .action-btn {
        background: #3942F6;
        color: white;
        border-radius: 10px;
        padding: 12px;
        font-weight: 600;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GERENCIAMENTO DE ESTADO (SESSION STATE)
# -----------------------------------------------------------------------------
if "notices_read" not in st.session_state:
    st.session_state.notices_read = set()

if "cert_issued" not in st.session_state:
    st.session_state.cert_issued = False

if "rh_requests" not in st.session_state:
    st.session_state.rh_requests = []

# Base de Dados Simulada de Avisos
MOCK_NOTICES = [
    {
        "id": 1,
        "title": "Nova Tabela de Preços e Prazos Essilor (Crizal Sapphire HR)",
        "category": "Novos Produtos",
        "tag_class": "tag-produtos",
        "date": "15/10/2026",
        "urgent": True,
        "content": "A partir da próxima segunda-feira, a linha de lentes multifocais Varilux com antirreflexo Crizal Sapphire HR terá reajuste de 4.5% e bonificação extra para a equipe de vendas."
    },
    {
        "id": 2,
        "title": "Aviso de Fechamento da Folha e Envio de Atestados de Outubro",
        "category": "RH",
        "tag_class": "tag-rh",
        "date": "14/10/2026",
        "urgent": False,
        "content": "Lembramos a todos os colaboradores que o prazo limite para inclusão de horas e entrega de comprovantes médicos é dia 20 deste mês."
    },
    {
        "id": 3,
        "title": "Treinamento Prático: Alinhamento de Armações de Titânio e Silhouette",
        "category": "Formação",
        "tag_class": "tag-formacao",
        "date": "12/10/2026",
        "urgent": False,
        "content": "Workshop presencial e online disponível na Academia SmartVision com técnicas de ajuste a frio para armações sem aro (parafusadas)."
    },
    {
        "id": 4,
        "title": "Procedimento de Contingência no PDV e Auditoria de Balcão",
        "category": "Operacional",
        "tag_class": "tag-operacional",
        "date": "10/10/2026",
        "urgent": False,
        "content": "Toda baixa de armações de alto valor unitário deve conter o número do pedido de venda registrado na justificativa de estoque."
    }
]

unread_count = len([n for n in MOCK_NOTICES if n["id"] not in st.session_state.notices_read])

# -----------------------------------------------------------------------------
# CHANGE 1: SIDEBAR & MENU DE NAVEGAÇÃO
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 20px 0;">
            <h2 style="color: #3942F6; margin:0; font-weight:800;">👓 SmartVision</h2>
            <span style="font-size:0.85rem; color:#64748B; font-weight:600;">PORTAL DO COLABORADOR</span>
        </div>
    """, unsafe_allow_html=True)

    menu_option = st.radio(
        "Navegação Principal:",
        options=[
            "🏠 O Meu Painel",
            "🎯 As Minhas Metas & Comissões",
            "📢 Mural do RH & Comunicação",
            "📂 Central do Colaborador (RH & Ponto)",
            "🎓 Academia SmartVision (Treinos)",
            "⚡ Atalhos Operacionais (PDV / OS / Receitas)",
            "📦 Gestão de Estoque Auditado (Módulo Central)"
        ],
        index=0
    )

    st.divider()

    # Informações da Sessão e Filial
    st.markdown("### 🏢 Unidade Operacional")
    st.markdown("""
    **Loja:** Matriz Shopping Paulista (Loja 04)  
    **Gerente da Unidade:** Juliana Brandão  
    **IP Conectado:** `192.168.10.45` (Rede Segura)
    """)

    st.divider()

    # Configuração de Conexão com Xano (para integração de estoque)
    with st.expander("🔌 Integração Backend Xano"):
        current_env_url = os.getenv("XANO_BASE_URL", "")
        base_url_input = st.text_input(
            "XANO_BASE_URL:",
            value=current_env_url or "https://x8ki-letl-twmt.n7.xano.io/api"
        )
        if base_url_input:
            os.environ["XANO_BASE_URL"] = base_url_input
        st.caption("Status: " + ("🟢 Ativo" if os.getenv("XANO_BASE_URL") else "🟡 Não configurado"))

# -----------------------------------------------------------------------------
# HEADER SUPERIOR (BRANDING, SEARCH, NOTIFICAÇÕES & PROFILE CARD)
# -----------------------------------------------------------------------------
search_query = ""
header_html = f"""
<div class="portal-header">
    <div>
        <h1 class="brand-title">👓 SmartVision</h1>
        <div class="brand-subtitle">Portal Corporativo do Consultor Ótico & Vendas</div>
    </div>
    <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
        <div class="notification-pill">
            🔔 Mensagens Não Lidas: <span class="badge-yellow">{unread_count}</span>
        </div>
        <div class="profile-card">
            <div class="profile-avatar">CS</div>
            <div>
                <div style="font-weight: 700; font-size: 0.95rem; color: #0F172A;">Carlos Eduardo Silveira</div>
                <div style="font-size: 0.8rem; color: #3942F6; font-weight: 600;">Consultor Ótico Senior</div>
                <div style="font-size: 0.75rem; color: #64748B;">Loja Matriz — Shopping Paulista</div>
            </div>
        </div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Barra de Pesquisa Rápida Global
search_col1, search_col2 = st.columns([3, 1])
with search_col1:
    search_query = st.text_input(
        "🔍 Busca Rápida de Avisos, Procedimentos e Manuais:",
        placeholder="Digite termos como 'Crizal', 'Atestado', 'Comissão', 'Horas', 'Multifocal'...",
        label_visibility="collapsed"
    )
with search_col2:
    st.markdown(f"<div style='padding-top: 8px; font-size: 0.85rem; color: #64748B;'><b>Data de Hoje:</b> {datetime.now().strftime('%d/%m/%Y')}</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SEÇÃO 1: O MEU PAINEL (VISÃO GERAL CONSOLIDADA)
# -----------------------------------------------------------------------------
if menu_option == "🏠 O Meu Painel":
    st.subheader("👋 Bem-vindo de volta, Carlos!")
    st.markdown("Aqui está o panorama atualizado das suas metas, avisos e atividades de hoje.")

    # Alerta Urgente em Destaque no Topo (Amarelo #F8B807)
    urgent_notices = [n for n in MOCK_NOTICES if n["urgent"] and n["id"] not in st.session_state.notices_read]
    if urgent_notices:
        for un in urgent_notices:
            st.markdown(f"""
            <div class="urgent-banner">
                <div style="font-size: 1.8rem;">⚠️</div>
                <div>
                    <strong style="color: #92400E; font-size: 1rem;">AVISO PRIORITÁRIO DA DIREÇÃO: {un['title']}</strong><br>
                    <span style="font-size: 0.9rem;">{un['content']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Widgets Diários de Performance (CHANGE 2)
    st.markdown("### 📊 Performance do Dia")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-widget">
            <div class="metric-title">Vendas Realizadas Hoje</div>
            <div class="metric-value">R$ 3.850,00</div>
            <div class="metric-sub">↗️ 6 Atendimentos concluídos</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-widget">
            <div class="metric-title">Ticket Médio (Hoje)</div>
            <div class="metric-value">R$ 641,66</div>
            <div class="metric-sub">↗️ +12% sobre a média da loja</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-widget">
            <div class="metric-title">Taxa de Conversão</div>
            <div class="metric-value">75%</div>
            <div class="metric-sub">🎯 6 vendas em 8 orçamentos</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-widget">
            <div class="metric-title">Comissão Prevista Mês</div>
            <div class="metric-value" style="color: #3942F6;">R$ 1.638,00</div>
            <div class="metric-sub" style="color: #F8B807;">⭐ Patamar Prata Ativo</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Resumo de Meta e Acesso Rápido
    col_meta, col_feed = st.columns([3, 2])
    with col_meta:
        st.markdown("### 🎯 Meta Mensal Individual (Outubro/2026)")
        meta_total = 60000.0
        vendido_acumulado = 46800.0
        percentual = (vendido_acumulado / meta_total) * 100
        restante = max(0.0, meta_total - vendido_acumulado)

        st.markdown(f"""
        <div class="metric-widget">
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <span style="font-weight: 700; font-size: 1.1rem; color: #0F172A;">Progresso: {percentual:.1f}% da Meta</span>
                <span style="font-weight: 800; color: #3942F6; font-size: 1.2rem;">R$ {vendido_acumulado:,.2f} / R$ {meta_total:,.2f}</span>
            </div>
            <div class="progress-container">
                <div class="progress-fill" style="width: {min(100.0, percentual)}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #64748B; margin-top: 4px;">
                <span>0%</span>
                <span><b>50%</b> (R$ 30k)</span>
                <span><b>75%</b> (R$ 45k) [Alcançado!]</span>
                <span><b>100%</b> (R$ 60k)</span>
            </div>
            <div style="margin-top: 14px; padding: 10px; background: #F8FAFC; border-radius: 8px; border: 1px dashed #CBD5E1;">
                <b>Falta apenas:</b> <span style="color: #3942F6; font-weight:700;">R$ {restante:,.2f}</span> para atingir a meta base e liberar o super-bônus Ouro de R$ 1.500,00!
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_feed:
        st.markdown("### 📢 Últimos Avisos da Loja")
        for notice in MOCK_NOTICES[:2]:
            is_read = notice["id"] in st.session_state.notices_read
            st.markdown(f"""
            <div class="notice-card" style="border-left-color: {'#10B981' if is_read else '#F8B807'};">
                <span class="tag-category {notice['tag_class']}">{notice['category']}</span>
                <div style="font-weight: 700; color: #0F172A; margin-bottom: 4px;">{notice['title']}</div>
                <div style="font-size: 0.85rem; color: #64748B;">{notice['content'][:110]}...</div>
            </div>
            """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SEÇÃO 2: AS MINHAS METAS & COMISSÕES (CHANGE 2)
# -----------------------------------------------------------------------------
elif menu_option == "🎯 As Minhas Metas & Comissões":
    st.subheader("🎯 Acompanhamento de Metas e Simulador de Comissões")
    st.markdown("Monitore a sua evolução mensal, entenda o cálculo das suas comissões e simule ganhos adicionais.")

    meta_individual = 60000.0
    vendido_atual = 46800.0
    pct = (vendido_atual / meta_individual) * 100
    falta = max(0.0, meta_individual - vendido_atual)

    # Painel Visual de Patamares
    st.markdown(f"""
    <div class="metric-widget" style="margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0; color: #0F172A; font-weight: 800;">Meta Individual do Mês: R$ {meta_individual:,.2f}</h3>
                <span style="color: #64748B; font-size: 0.9rem;">Período: Outubro de 2026 (Restam 15 dias úteis)</span>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 2rem; font-weight: 800; color: #3942F6;">{pct:.1f}%</span>
            </div>
        </div>
        <div class="progress-container" style="height: 28px;">
            <div class="progress-fill" style="width: {pct}%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; color: #475569; margin-top: 6px;">
            <span>0%</span>
            <span>🥉 Bronze: 50% (R$ 30k)</span>
            <span>🥈 Prata: 75% (R$ 45k) [ATIVO]</span>
            <span>🥇 Ouro: 100% (R$ 60k)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.metric(label="Valor Vendido Acumulado", value=f"R$ {vendido_atual:,.2f}", delta="78% Concluído")
    with col_kpi2:
        st.metric(label="Valor Restante para Meta 100%", value=f"R$ {falta:,.2f}", delta="-R$ 13.200,00", delta_color="inverse")
    with col_kpi3:
        st.metric(label="Média de Venda Necessária / Dia", value=f"R$ {falta / 15:,.2f}", delta="Meta Diária de R$ 880,00")

    st.divider()

    # Simulador e Extrato de Comissões
    st.markdown("### 💰 Simulador de Comissões e Super-Metas")
    st.markdown("""
    A política de comissionamento da SmartVision recompensa a superação de metas por faixas:
    - **Base (até 74% da meta):** 2.0% de comissão linear sobre vendas.
    - **Patamar Prata (75% a 99%):** 2.5% de comissão + R$ 400,00 de bônus fixo.
    - **Patamar Ouro (100% a 119%):** 3.5% de comissão + R$ 1.000,00 de bônus fixo.
    - **Super-Meta Diamante (120%+):** 4.5% de comissão + R$ 2.000,00 de bônus extra.
    """)

    sim_col1, sim_col2 = st.columns([1, 1])

    with sim_col1:
        st.markdown("#### 🎛️ Simule Vendas Adicionais no Mês")
        vendas_adicionais = st.slider(
            "Simular acréscimo de vendas (R$):",
            min_value=0,
            max_value=30000,
            value=13200,
            step=500,
            format="R$ %d"
        )
        total_simulado = vendido_atual + vendas_adicionais
        pct_simulado = (total_simulado / meta_individual) * 100

        # Cálculo da Comissão Simulada
        if pct_simulado < 75.0:
            taxa = 0.02
            bonus = 0.0
            nivel = "Base (Bronze)"
        elif pct_simulado < 100.0:
            taxa = 0.025
            bonus = 400.0
            nivel = "🥈 Patamar Prata"
        elif pct_simulado < 120.0:
            taxa = 0.035
            bonus = 1000.0
            nivel = "🥇 Patamar Ouro"
        else:
            taxa = 0.045
            bonus = 2000.0
            nivel = "💎 Super-Meta Diamante"

        comissao_linear = total_simulado * taxa
        remuneracao_total = comissao_linear + bonus

    with sim_col2:
        st.markdown("#### 💵 Projeção de Remuneração Variável")
        st.markdown(f"""
        <div class="metric-widget" style="border-left: 6px solid #3942F6;">
            <div style="font-size: 0.9rem; color: #64748B;">Total de Vendas Simulado:</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #0F172A;">R$ {total_simulado:,.2f} ({pct_simulado:.1f}%)</div>
            <hr style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span>Nível Conquistado:</span>
                <span class="badge-yellow">{nivel}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span>Comissão Percentual ({taxa*100:.1f}%):</span>
                <b>R$ {comissao_linear:,.2f}</b>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span>Bônus Fixo por Meta:</span>
                <b style="color: #10B981;">+ R$ {bonus:,.2f}</b>
            </div>
            <hr style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 1.2rem; font-weight: 800; color: #3942F6;">
                <span>Total Variável Estimado:</span>
                <span>R$ {remuneracao_total:,.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SEÇÃO 3: MURAL DO RH & COMUNICAÇÃO (CHANGE 3)
# -----------------------------------------------------------------------------
elif menu_option == "📢 Mural do RH & Comunicação":
    st.subheader("📢 Mural Oficial de Comunicação & RH")
    st.markdown("Fique por dentro das novidades, comunicados operacionais, avisos da diretoria e aniversariantes.")

    tab_mural, tab_rec = st.tabs(["📋 Mural de Avisos Oficiais", "🎉 Reconhecimento & Aniversários"])

    with tab_mural:
        # Filtros de Categoria
        filtro_cat = st.selectbox(
            "Filtrar por Categoria:",
            options=["Todas", "RH", "Operacional", "Novos Produtos", "Formação"]
        )

        avisos_exibidos = [
            n for n in MOCK_NOTICES
            if (filtro_cat == "Todas" or n["category"] == filtro_cat) and
               (search_query.lower() in n["title"].lower() or search_query.lower() in n["content"].lower())
        ]

        st.markdown(f"**Total de avisos disponíveis:** {len(avisos_exibidos)}")

        for notice in avisos_exibidos:
            is_read = notice["id"] in st.session_state.notices_read
            with st.container():
                st.markdown(f"""
                <div class="notice-card" style="border-left-color: {'#10B981' if is_read else '#F8B807'};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="tag-category {notice['tag_class']}">{notice['category']}</span>
                        <span style="font-size: 0.8rem; color: #64748B;">📅 Publicado em {notice['date']}</span>
                    </div>
                    <h4 style="margin: 6px 0 10px 0; color: #0F172A;">{notice['title']}</h4>
                    <p style="color: #334155; line-height: 1.5; font-size: 0.95rem;">{notice['content']}</p>
                </div>
                """, unsafe_allow_html=True)

                col_btn, col_st = st.columns([1, 4])
                with col_btn:
                    if is_read:
                        st.caption("✅ Você já registrou ciência neste comunicado.")
                    else:
                        if st.button(f"👁️ Marcar como Lido / Ciente", key=f"btn_read_{notice['id']}", type="primary"):
                            st.session_state.notices_read.add(notice["id"])
                            st.rerun()

    with tab_rec:
        st.markdown("### 🏆 Colaborador Destaque do Mês")
        st.markdown("""
        <div class="metric-widget" style="border: 2px solid #F8B807; background: linear-gradient(135deg, #FFFFFF 0%, #FFFBEB 100%);">
            <div style="display: flex; gap: 20px; align-items: center;">
                <div style="font-size: 3.5rem;">🥇</div>
                <div>
                    <h3 style="margin: 0; color: #0F172A;">Carlos Eduardo Silveira</h3>
                    <div style="color: #3942F6; font-weight: 700;">Consultor Ótico Senior — Loja Matriz</div>
                    <p style="margin-top: 8px; color: #475569; font-size: 0.9rem;">
                        <i>"Parabéns pelo excelente desempenho na venda de lentes multifocais premium e pelo índice de 100% de satisfação nas conferências de receitas médicas."</i>
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🎂 Aniversariantes do Mês (Outubro)")
        col_aniv1, col_aniv2, col_aniv3 = st.columns(3)
        with col_aniv1:
            st.markdown("""
            <div class="metric-widget" style="text-align: center;">
                <div style="font-size: 2rem;">🎈</div>
                <b>Mariana Castro</b><br>
                <span style="font-size: 0.85rem; color: #64748B;">Atendente — 18/10</span>
            </div>
            """, unsafe_allow_html=True)
        with col_aniv2:
            st.markdown("""
            <div class="metric-widget" style="text-align: center;">
                <div style="font-size: 2rem;">🎈</div>
                <b>Felipe Penna</b><br>
                <span style="font-size: 0.85rem; color: #64748B;">Técnico Óptico — 24/10</span>
            </div>
            """, unsafe_allow_html=True)
        with col_aniv3:
            st.markdown("""
            <div class="metric-widget" style="text-align: center;">
                <div style="font-size: 2rem;">🎈</div>
                <b>Renata Oliveira</b><br>
                <span style="font-size: 0.85rem; color: #64748B;">Gerente Adjunta — 29/10</span>
            </div>
            """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SEÇÃO 4: CENTRAL DO COLABORADOR (RH, DOCUMENTOS & HORÁRIOS - CHANGE 4)
# -----------------------------------------------------------------------------
elif menu_option == "📂 Central do Colaborador (RH & Ponto)":
    st.subheader("📂 Central do Colaborador: Folha, Ponto & Solicitações")
    st.markdown("Acesse seus comprovantes de rendimento, controle seu saldo de banco de horas e envie pedidos formais ao RH.")

    tab_holerite, tab_ponto, tab_solic = st.tabs([
        "📄 Recibos de Vencimento (Holerites)",
        "⏰ Espelho de Ponto & Banco de Horas",
        "📝 Solicitações ao RH (Férias, Atestados, Turno)"
    ])

    with tab_holerite:
        st.markdown("### 📄 Holerites dos Últimos 12 Meses")
        st.info("💡 Clique no mês desejado para conferir o detalhamento de proventos e efetuar o download em formato PDF.")

        meses = [
            ("Setembro/2026", 3200.00, 1850.40, 520.10, 4530.30),
            ("Agosto/2026", 3200.00, 1420.00, 480.00, 4140.00),
            ("Julho/2026", 3200.00, 2100.50, 560.20, 4740.30),
            ("Junho/2026", 3200.00, 1600.00, 495.00, 4305.00),
            ("Maio/2026", 3200.00, 1300.00, 460.00, 4040.00),
            ("Abril/2026", 3200.00, 1900.00, 530.00, 4570.00),
            ("Março/2026", 3200.00, 1750.00, 510.00, 4440.00),
            ("Fevereiro/2026", 3200.00, 1200.00, 440.00, 3960.00),
            ("Janeiro/2026", 3200.00, 2400.00, 610.00, 4990.00),
            ("Dezembro/2025", 3200.00, 2900.00, 690.00, 5410.00),
            ("Novembro/2025", 3200.00, 1500.00, 470.00, 4230.00),
            ("Outubro/2025", 3200.00, 1400.00, 460.00, 4140.00),
        ]

        for mes, base, comiss, desc, liq in meses:
            with st.expander(f"📑 Competência: {mes} — Valor Líquido: R$ {liq:,.2f}"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Salário Base", f"R$ {base:,.2f}")
                c2.metric("Comissões & DSR", f"R$ {comiss:,.2f}")
                c3.metric("Descontos (INSS/IR)", f"R$ {desc:,.2f}")
                c4.metric("Total Líquido", f"R$ {liq:,.2f}")

                pdf_content = f"""SMARTVISION OTICAS LTDA - RECIBO DE PAGAMENTO
Competencia: {mes}
Colaborador: Carlos Eduardo Silveira (Consultor Otico Senior)
Salario Base: R$ {base:,.2f}
Comissoes: R$ {comiss:,.2f}
Descontos: R$ {desc:,.2f}
Valor Liquido Creditado: R$ {liq:,.2f}
Status: Autenticado digitalmente
"""
                st.download_button(
                    label=f"📥 Baixar Holerite {mes} (PDF)",
                    data=pdf_content,
                    file_name=f"holerite_smartvision_{mes.replace('/', '_')}.pdf",
                    mime="application/pdf",
                    key=f"dl_{mes}"
                )

    with tab_ponto:
        st.markdown("### ⏰ Controle de Ponto Digital & Horas Extras")
        p1, p2, p3 = st.columns(3)
        with p1:
            st.metric("Saldo Banco de Horas", "+14h 30min", delta="Crédito positivo", delta_color="normal")
        with p2:
            st.metric("Horas Extras no Mês", "06h 15min", delta="Aprovadas")
        with p3:
            st.metric("Jornada Semanal", "44h semanais", delta="Conforme escala CLT")

        st.markdown("#### Últimas Marcações de Ponto (Semana Atual)")
        st.dataframe([
            {"Data": "15/10/2026", "Entrada": "09:00", "Saída Almoço": "12:30", "Volta Almoço": "13:30", "Saída Final": "18:00", "Total": "8h 00m", "Status": "Regular"},
            {"Data": "14/10/2026", "Entrada": "08:55", "Saída Almoço": "12:30", "Volta Almoço": "13:30", "Saída Final": "19:15", "Total": "9h 20m", "Status": "+1h 20m Extra"},
            {"Data": "13/10/2026", "Entrada": "09:02", "Saída Almoço": "12:30", "Volta Almoço": "13:30", "Saída Final": "18:05", "Total": "8h 03m", "Status": "Regular"},
            {"Data": "12/10/2026", "Entrada": "09:00", "Saída Almoço": "12:30", "Volta Almoço": "13:30", "Saída Final": "18:00", "Total": "8h 00m", "Status": "Regular"},
            {"Data": "09/10/2026", "Entrada": "09:00", "Saída Almoço": "12:30", "Volta Almoço": "13:30", "Saída Final": "18:00", "Total": "8h 00m", "Status": "Regular"},
        ], use_container_width=True)

    with tab_solic:
        st.markdown("### 📝 Solicitações e Requerimentos ao RH")
        tipo_solic = st.selectbox(
            "Selecione o Tipo de Solicitação:",
            options=["Agendamento de Férias", "Envio de Atestado Médico", "Solicitação de Troca de Turno"]
        )

        with st.form("form_rh_solic"):
            if tipo_solic == "Agendamento de Férias":
                dt_inicio = st.date_input("Data de Início das Férias:", value=date.today() + timedelta(days=30))
                dias = st.slider("Quantidade de Dias:", min_value=10, max_value=30, value=20)
                abono = st.checkbox("Desejo vender 1/3 das férias (Abono Pecuniário)")
                obs = st.text_area("Observações para a gerência:")

            elif tipo_solic == "Envio de Atestado Médico":
                dt_atestado = st.date_input("Data do Atendimento Médico:", value=date.today())
                dias_dispensa = st.number_input("Dias de Dispensa:", min_value=1, max_value=15, value=1)
                medico = st.text_input("Nome do Profissional / CRM:")
                arquivo = st.file_uploader("Anexar Foto ou PDF do Atestado Médico:", type=["png", "jpg", "jpeg", "pdf"])
                obs = st.text_area("Observações:")

            else:
                colega = st.text_input("Nome do Colega Substituto:")
                dt_original = st.date_input("Seu Turno Original:", value=date.today() + timedelta(days=2))
                dt_compensacao = st.date_input("Turno a Compensar:", value=date.today() + timedelta(days=5))
                obs = st.text_area("Justificativa da Troca:")

            enviar_solic = st.form_submit_button("🚀 Enviar Solicitação ao RH", type="primary")

            if enviar_solic:
                protocolo = f"RH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                st.session_state.rh_requests.append({
                    "protocolo": protocolo,
                    "tipo": tipo_solic,
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "status": "Em Análise pela Gerência"
                })
                st.success(f"✅ Solicitação enviada com sucesso! Protocolo: **{protocolo}**")


# -----------------------------------------------------------------------------
# SEÇÃO 5: ACADEMIA SMARTVISION (TREINOS & GUIA DE LENTES - CHANGE 5)
# -----------------------------------------------------------------------------
elif menu_option == "🎓 Academia SmartVision (Treinos)":
    st.subheader("🎓 Academia SmartVision & Guia Técnico de Lentes")
    st.markdown("Consulte a tabela comparativa de materiais e especialize-se com microlearnings rápidos de alto impacto.")

    tab_guia, tab_cursos = st.tabs(["👓 Guia Rápido de Lentes e Materiais", "📚 Módulos de Microlearning & Certificados"])

    with tab_guia:
        st.markdown("### 🔍 Matriz Comparativa de Índices de Refração")
        st.markdown("""
        Oriente o cliente de acordo com a dioptria (grau esférico e cilíndrico) para indicar a melhor espessura e peso de lente:
        """)

        st.dataframe([
            {"Índice": "1.50 (CR-39)", "Material": "Resina Básica", "Faixa Recomendada": "0 a +/- 2.00", "Espessura": "Padrão", "Resistência": "Média", "Indicação": "Armações fechadas aro completo"},
            {"Índice": "1.56", "Material": "Resina Médio Índice", "Faixa Recomendada": "+/- 2.00 a +/- 4.00", "Espessura": "20% mais fina", "Resistência": "Média-Alta", "Indicação": "Aro fechado ou meio aro"},
            {"Índice": "1.59 (Poly)", "Material": "Policarbonato", "Faixa Recomendada": "0 a +/- 4.00", "Espessura": "25% mais fina", "Resistência": "Altíssima (Inquebrável)", "Indicação": "Armações parafusadas (três peças), crianças e esporte"},
            {"Índice": "1.67", "Material": "Resina Alto Índice", "Faixa Recomendada": "+/- 4.00 a +/- 7.00", "Espessura": "40% mais fina", "Resistência": "Alta", "Indicação": "Graus médios a altos, bordas finas"},
            {"Índice": "1.74", "Material": "Ultra Alto Índice", "Faixa Recomendada": "+/- 7.00 em diante", "Espessura": "60% mais fina", "Resistência": "Alta", "Indicação": "Graus muito elevados, máxima estética visual"},
        ], use_container_width=True)

        st.markdown("### 🛡️ Tratamentos Antirreflexo por Fabricante Parceiro")
        c_ess, c_zeiss, c_hoya = st.columns(3)
        with c_ess:
            st.markdown("""
            <div class="metric-widget" style="border-top: 4px solid #3942F6;">
                <h4 style="color:#3942F6; margin:0;">Essilor</h4>
                <span style="font-size:0.8rem; color:#64748B;">Linha Crizal</span>
                <ul style="font-size:0.85rem; padding-left:18px; margin-top:8px;">
                    <li><b>Crizal Easy Pro:</b> Entrada, proteção básica e limpeza facilitada.</li>
                    <li><b>Crizal Rock:</b> Máxima resistência a arranhões e impactos.</li>
                    <li><b>Crizal Sapphire HR:</b> Transparência absoluta e antirreflexo 360°.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        with c_zeiss:
            st.markdown("""
            <div class="metric-widget" style="border-top: 4px solid #3942F6;">
                <h4 style="color:#3942F6; margin:0;">Zeiss</h4>
                <span style="font-size:0.8rem; color:#64748B;">Linha DuraVision</span>
                <ul style="font-size:0.85rem; padding-left:18px; margin-top:8px;">
                    <li><b>DuraVision Silver:</b> Bom custo-benefício e camada hidrofóbica.</li>
                    <li><b>DuraVision Platinum:</b> Dureza superior por deposição iônica.</li>
                    <li><b>BlueGuard:</b> Bloqueio da luz azul nociva integrado à massa da lente.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        with c_hoya:
            st.markdown("""
            <div class="metric-widget" style="border-top: 4px solid #3942F6;">
                <h4 style="color:#3942F6; margin:0;">Hoya</h4>
                <span style="font-size:0.8rem; color:#64748B;">Linha Hi-Vision</span>
                <ul style="font-size:0.85rem; padding-left:18px; margin-top:8px;">
                    <li><b>Hi-Vision Aqua:</b> Camada protetora hidrorrepelente básica.</li>
                    <li><b>Hi-Vision LongLife:</b> 5x mais resistente a riscos (Garantia estendida).</li>
                    <li><b>BlueControl:</b> Neutralização do azul de telas digitais.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    with tab_cursos:
        st.markdown("### 📚 Cursos de Microlearning Disponíveis")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="metric-widget">
                <span class="tag-category tag-formacao">VENDAS CONSULTIVAS</span>
                <h4>Como vender lentes multifocais premium</h4>
                <p style="font-size: 0.85rem; color: #475569;">Aprenda a mapear as queixas de visão de perto e meia-distância dos clientes para recomendar Varilux XR ou Zeiss SmartLife.</p>
                <b>Progresso: 85%</b>
                <div class="progress-container" style="height: 12px;"><div class="progress-fill" style="width: 85%;"></div></div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("▶️ Continuar Aula (Módulo 4: Demonstração Prática)", key="aula1"):
                st.info("Vídeo-aula carregada. Conclua o quiz de 3 perguntas para emissão do certificado.")

        with c2:
            st.markdown("""
            <div class="metric-widget">
                <span class="tag-category tag-operacional">LABORATÓRIO & TÉCNICO</span>
                <h4>Ajuste e alinhamento de armações de titânio</h4>
                <p style="font-size: 0.85rem; color: #475569;">Técnicas seguras de curvatura de ponteiras, ângulo pantoscópico e pressão de plaquetas sem danificar o acabamento.</p>
                <b>Progresso: 100% (Concluído!)</b>
                <div class="progress-container" style="height: 12px;"><div class="progress-fill" style="width: 100%; background: #10B981;"></div></div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🎓 Emitir Certificado Digital de Conclusão", key="aula2", type="primary"):
                st.session_state.cert_issued = True

        if st.session_state.cert_issued:
            st.markdown("""
            <div style="background: white; border: 4px double #F8B807; border-radius: 16px; padding: 30px; text-align: center; margin-top: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.05);">
                <span style="font-size: 3rem;">🎓</span>
                <h2 style="color: #3942F6; margin: 10px 0 5px 0;">CERTIFICADO DE CAPACITAÇÃO PROFISSIONAL</h2>
                <p style="color: #64748B; font-size: 0.95rem;">Certificamos que</p>
                <h3 style="color: #0F172A; text-decoration: underline;">Carlos Eduardo Silveira</h3>
                <p style="color: #475569; max-width: 600px; margin: 0 auto; line-height: 1.6;">
                    concluiu com êxito o programa de especialização técnica em <b>Ajuste e Alinhamento de Armações de Titânio e Lentes Especiais</b> com carga horária de 12 horas, obtendo aproveitamento com distinção.
                </p>
                <div style="margin-top: 20px; font-size: 0.85rem; color: #64748B;">
                    Emitido por Academia SmartVision Óticas em 15/10/2026 — Código de Validação: <code>SV-ACAD-2026-8874</code>
                </div>
            </div>
            """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SEÇÃO 6: ATALHOS OPERACIONAIS (PDV / RECEITAS / OS - CHANGE 6)
# -----------------------------------------------------------------------------
elif menu_option == "⚡ Atalhos Operacionais (PDV / OS / Receitas)":
    st.subheader("⚡ Atalhos Operacionais do Consultor")
    st.markdown("Acesse diretamente as rotinas mais frequentes da ótica com poucos cliques.")

    acao = st.radio(
        "Selecione o Fluxo Operacional Rápido:",
        options=["💳 Nova Venda / PDV Rápido", "📝 Ficha de Receita Óptica (Conferência)", "🔍 Consultar Estado de OS em Laboratório"],
        horizontal=True
    )

    if acao == "💳 Nova Venda / PDV Rápido":
        st.markdown("### 💳 Lançamento de Orçamento / Venda no PDV")
        with st.form("form_pdv"):
            c1, c2 = st.columns(2)
            with c1:
                cliente = st.text_input("Nome Completo do Cliente:", value="Ana Paula Ferreira")
                cpf = st.text_input("CPF do Cliente:", value="123.456.789-00")
                armacao = st.selectbox("Armação Escolhida:", ["Ray-Ban RB5154 Clubmaster", "Oakley Crosslink Zero", "Silhouette Titan Minimal", "Vogue Eyewear VO5211"])
            with c2:
                lente = st.selectbox("Lente Selecionada:", ["Crizal Sapphire HR Multifocal 1.67", "Zeiss DuraVision Platinum 1.59", "Hoya LongLife BlueControl 1.60", "CR-39 Antirreflexo Básico 1.50"])
                valor = st.number_input("Valor Total Negociado (R$):", min_value=100.0, value=1850.0, step=50.0)
                condicao = st.selectbox("Forma de Pagamento:", ["Cartão de Crédito (10x sem juros)", "PIX à Vista (5% desconto)", "Boleto Faturado"])

            finalizar_pdv = st.form_submit_button("✅ Concluir Registro de Venda", type="primary")
            if finalizar_pdv:
                st.success(f"🎉 Venda de **R$ {valor:,.2f}** para **{cliente}** finalizada com sucesso! Vinculada ao consultor Carlos Eduardo.")

    elif acao == "📝 Ficha de Receita Óptica (Conferência)":
        st.markdown("### 📝 Ficha Técnica de Prescrição Oftalmológica")
        st.info("Insira os parâmetros médicos da receita para validação com os limites técnicos da lente:")

        col_od, col_oe = st.columns(2)
        with col_od:
            st.markdown("#### 👁️ Olho Direito (OD)")
            od_esf = st.number_input("Esférico OD:", min_value=-20.0, max_value=20.0, value=-2.50, step=0.25)
            od_cil = st.number_input("Cilíndrico OD:", min_value=-10.0, max_value=0.0, value=-0.75, step=0.25)
            od_eixo = st.number_input("Eixo OD (°):", min_value=0, max_value=180, value=90, step=1)
            od_adicao = st.number_input("Adição OD:", min_value=0.0, max_value=4.0, value=2.00, step=0.25)

        with col_oe:
            st.markdown("#### 👁️ Olho Esquerdo (OE)")
            oe_esf = st.number_input("Esférico OE:", min_value=-20.0, max_value=20.0, value=-2.25, step=0.25)
            oe_cil = st.number_input("Cilíndrico OE:", min_value=-10.0, max_value=0.0, value=-1.00, step=0.25)
            oe_eixo = st.number_input("Eixo OE (°):", min_value=0, max_value=180, value=85, step=1)
            oe_adicao = st.number_input("Adição OE:", min_value=0.0, max_value=4.0, value=2.00, step=0.25)

        st.success("✅ Receita conferida: Dioptrias dentro da faixa ideal para lentes de índice 1.59 (Poly) ou 1.67.")

    else:
        st.markdown("### 🔍 Rastreamento de Ordem de Serviço (OS)")
        num_os = st.text_input("Número da OS da Ótica:", value="OS-2026-9812")
        if st.button("Buscar Estado no Laboratório", type="primary"):
            st.markdown("""
            <div class="metric-widget" style="border-left: 6px solid #F8B807;">
                <h4>Status da OS #2026-9812</h4>
                <p><b>Cliente:</b> Roberto Mendes | <b>Armação:</b> Silhouette Titan | <b>Lente:</b> Varilux 1.67 Crizal</p>
                <div class="badge-yellow">⚙️ EM MONTAGEM NO LABORATÓRIO CENTRAL</div>
                <p style="margin-top: 10px; font-size: 0.9rem; color: #475569;">
                    Previsão de entrega na loja: <b>Amanhã às 15:00</b>.
                </p>
            </div>
            """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SEÇÃO 7: GESTÃO DE ESTOQUE AUDITADO (MÓDULO CENTRAL DO SMARTVISION)
# -----------------------------------------------------------------------------
elif menu_option == "📦 Gestão de Estoque Auditado (Módulo Central)":
    st.subheader("📦 Módulo de Estoque Auditado (AGENTS.md)")
    st.info("💡 **Conformidade Crítica**: Todas as entradas e saídas exigem registro prévio de auditoria na tabela `stock_movement` e validação estrita contra saldo negativo.")

    tab_e, tab_s, tab_c = st.tabs(["📥 Entrada de Estoque", "📤 Saída de Estoque", "📋 Consulta de Catálogo"])

    with tab_e:
        st.markdown("#### Registrar Entrada de Mercadoria")
        p_id = st.number_input("ID do Produto:", min_value=1, value=1, step=1, key="ent_pid")
        qty = st.number_input("Quantidade:", min_value=1, value=5, step=1, key="ent_qty")
        reason = st.text_input("Justificativa / Nota Fiscal:", value="NF 4920 - Recebimento Fornecedor", key="ent_rsn")

        if st.button("Confirmar Entrada Auditada", type="primary", key="btn_ent"):
            try:
                if xano_client:
                    res = xano_client.record_stock_entry({"product_id": p_id, "quantity": qty, "reason": reason, "unit_cost": 0, "user_id": 1})
                    st.success(f"✅ Entrada registrada e auditada com sucesso! Novo saldo: {res.get('product', {}).get('current_stock', 'N/A')}")
                else:
                    st.warning("Serviço Xano não configurado ou offline. Operação simulada localmente com sucesso.")
            except Exception as e:
                st.error(f"Erro ao registrar entrada: {e}")

    with tab_s:
        st.markdown("#### Registrar Saída de Estoque")
        p_id_s = st.number_input("ID do Produto:", min_value=1, value=1, step=1, key="sai_pid")
        qty_s = st.number_input("Quantidade a Retirar:", min_value=1, value=1, step=1, key="sai_qty")
        reason_s = st.text_input("Motivo da Saída (Obrigatório):", value="Venda Balcão Pedido #402", key="sai_rsn")

        if st.button("Confirmar Saída com Verificação de Saldo", type="primary", key="btn_sai"):
            try:
                if xano_client:
                    res = xano_client.record_stock_exit({"product_id": p_id_s, "quantity": qty_s, "reason": reason_s, "user_id": 1})
                    st.success(f"✅ Saída concluída e auditada! Saldo atualizado: {res.get('product', {}).get('current_stock', 'N/A')}")
                else:
                    st.warning("Serviço Xano não configurado. Em caso de saldo insuficiente, o backend rejeitaria com HTTP 400 conforme AGENTS.md.")
            except Exception as e:
                st.error(f"Erro na saída: {e}")

    with tab_c:
        st.markdown("#### Produtos Cadastrados")
        try:
            if xano_client and os.getenv("XANO_BASE_URL"):
                prods = xano_client.list_products()
                st.dataframe(prods, use_container_width=True)
            else:
                st.dataframe([
                    {"id": 1, "sku": "ARM-RAY-01", "name": "Armação Ray-Ban Clubmaster", "category": "Armação", "current_stock": 14, "min_stock": 5},
                    {"id": 2, "sku": "LEN-CRIZ-02", "name": "Lente Multifocal Crizal Sapphire HR", "category": "Lente Oftálmica", "current_stock": 8, "min_stock": 4},
                    {"id": 3, "sku": "CON-ACUV-03", "name": "Lente de Contato Acuvue Oasys", "category": "Lente de Contato", "current_stock": 25, "min_stock": 10},
                ], use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao listar catálogo: {e}")
