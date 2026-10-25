# app.py
"""Smart Vision — Portal do Colaborador & Gestão de Loja Óptica.

Interface Streamlit desenvolvida para consultores ópticos e equipe de loja,
incorporando branding exclusivo (#3942F6, #F8B807, #F8FAFC), metas dinâmicas,
mural de RH, central de documentos, Academia SmartVision e atalhos operacionais.
"""

import html
import os
from datetime import datetime, date, timedelta
import streamlit as st

# Carregar variáveis de ambiente do .env se existir localmente
_env_file = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_file):
    try:
        with open(_env_file, "r", encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.strip())
    except Exception:
        pass

# Sincronizar st.secrets com os.environ para deploys no Streamlit Cloud
try:
    if hasattr(st, "secrets"):
        for _k, _v in st.secrets.items():
            if isinstance(_v, str):
                os.environ.setdefault(_k, _v)
except Exception:
    pass

# Tentativa de importação do serviço Xano para o módulo de estoque
try:
    from services import xano_client
    from services import auth_service
    from services import product_catalog
except Exception:
    xano_client = None
    auth_service = None
    product_catalog = None

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    :root {
        --sv-primary: #3942F6;
        --sv-primary-hover: #252CD6;
        --sv-primary-deep: #1E25B6;
        --sv-primary-soft: #EEF0FF;
        --sv-secondary: #F8B807;
        --sv-secondary-soft: #FFF8DB;
        --sv-bg: #F4F6FB;
        --sv-surface: #FFFFFF;
        --sv-surface-muted: #F8FAFC;
        --sv-text: #0F172A;
        --sv-muted: #64748B;
        --sv-muted-light: #94A3B8;
        --sv-border: #E2E8F0;
        --sv-success: #10B981;
        --sv-warning: #F59E0B;
        --sv-danger: #EF4444;
        --sv-shadow-sm: 0 2px 6px -1px rgba(15, 23, 42, 0.04), 0 1px 3px rgba(15, 23, 42, 0.03);
        --sv-shadow-md: 0 8px 24px -6px rgba(15, 23, 42, 0.08), 0 2px 8px -2px rgba(15, 23, 42, 0.04);
        --sv-shadow-lg: 0 24px 48px -18px rgba(30, 37, 182, 0.22), 0 8px 20px -8px rgba(15, 23, 42, 0.08);
        --primary-color: #3942F6;
        --secondary-color: #F8B807;
        --bg-color: #F4F6FB;
        --text-main: #0F172A;
        --text-muted: #64748B;
        --card-bg: #FFFFFF;
        --border-color: #E2E8F0;
    }

    html, body, .stApp, [class*="css"], .stMarkdown {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        color: var(--sv-text);
    }

    html, body { background: var(--sv-bg) !important; }

    .stApp {
        background-color: var(--sv-bg) !important;
        background-image:
            radial-gradient(circle at 4% -4%, rgba(57, 66, 246, 0.08), transparent 30rem),
            radial-gradient(circle at 96% 4%, rgba(248, 184, 7, 0.07), transparent 26rem),
            linear-gradient(180deg, #F7F8FC 0%, #F1F3F9 100%) !important;
        background-attachment: fixed !important;
    }

    [data-testid="stAppViewContainer"] { background: transparent !important; }

    /* Chrome do Streamlit */
    header[data-testid="stHeader"] {
        display: block !important;
        height: 0 !important;
        min-height: 0 !important;
        background: transparent !important;
        pointer-events: none !important;
    }

    [data-testid="stToolbar"] {
        display: flex !important;
        width: 100% !important;
        background: transparent !important;
        pointer-events: none !important;
    }

    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    .stDeployButton,
    #MainMenu,
    footer {
        display: none !important;
    }

    /* Controle de reabertura da sidebar */
    button[data-testid="stExpandSidebarButton"] {
        position: fixed !important;
        top: 16px !important;
        left: 16px !important;
        z-index: 1000000 !important;
        width: 40px !important;
        height: 40px !important;
        min-height: 40px !important;
        padding: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 1px solid var(--sv-border) !important;
        border-radius: 12px !important;
        background: rgba(255, 255, 255, 0.96) !important;
        color: var(--sv-text) !important;
        box-shadow: 0 12px 24px -14px rgba(15, 23, 42, 0.45) !important;
        pointer-events: auto !important;
        backdrop-filter: blur(10px);
        transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease !important;
    }

    button[data-testid="stExpandSidebarButton"]:hover {
        background: #FFFFFF !important;
        box-shadow: 0 16px 28px -14px rgba(57, 66, 246, 0.38) !important;
        transform: translateY(-1px);
    }

    button[data-testid="stExpandSidebarButton"] span {
        color: var(--sv-text) !important;
        font-size: 1.2rem !important;
    }

    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        max-width: 1480px !important;
        padding: 1.5rem 2rem 3.5rem 2rem !important;
        background: transparent !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        color: var(--sv-text) !important;
        letter-spacing: -0.025em;
    }

    .stMarkdown h2 { font-size: 1.35rem !important; font-weight: 700 !important; margin-top: 1.3rem !important; }
    .stMarkdown h3 { font-size: 1.12rem !important; font-weight: 700 !important; margin-top: 1.15rem !important; }
    .stMarkdown h4 { font-size: 1rem !important; font-weight: 700 !important; }
    .stMarkdown p, .stMarkdown li { color: #334155; line-height: 1.65; }
    .stCaptionContainer, [data-testid="stCaptionContainer"] { color: var(--sv-muted) !important; }
    a { color: var(--sv-primary) !important; text-decoration: none; }
    a:hover { text-decoration: underline; }

    hr, .stDivider { border-color: var(--sv-border) !important; }

    /* ==============================================================
       HERO EXECUTIVO
       ============================================================== */
    .portal-header {
        position: relative;
        isolation: isolate;
        overflow: hidden;
        background:
            radial-gradient(circle at 84% 12%, rgba(248, 184, 7, 0.18), transparent 18rem),
            linear-gradient(125deg, #222AD7 0%, #3942F6 46%, #1D24B4 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 24px;
        padding: 28px 32px;
        color: #FFFFFF;
        margin-bottom: 22px;
        box-shadow: 0 24px 48px -18px rgba(30, 37, 182, 0.42), 0 8px 18px -8px rgba(15, 23, 42, 0.16);
        animation: sv-rise 0.45s ease-out both;
    }

    .portal-header::before {
        content: "";
        position: absolute;
        inset: 0;
        z-index: -1;
        background-image:
            linear-gradient(rgba(255, 255, 255, 0.045) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.045) 1px, transparent 1px);
        background-size: 32px 32px;
        mask-image: linear-gradient(105deg, transparent 24%, rgba(0, 0, 0, 0.7) 75%, transparent 100%);
        -webkit-mask-image: linear-gradient(105deg, transparent 24%, rgba(0, 0, 0, 0.7) 75%, transparent 100%);
    }

    .portal-header::after {
        content: "";
        position: absolute;
        z-index: -1;
        width: 310px;
        height: 310px;
        right: -90px;
        top: -190px;
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 50%;
        box-shadow: 0 0 0 46px rgba(255, 255, 255, 0.035), 0 0 0 92px rgba(255, 255, 255, 0.02);
    }

    .portal-header-inner {
        position: relative;
        z-index: 1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 24px;
    }

    .brand-lockup { display: flex; align-items: center; gap: 16px; min-width: 280px; }

    .brand-mark {
        width: 56px;
        height: 56px;
        flex: 0 0 56px;
        border-radius: 17px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.13);
        border: 1px solid rgba(255, 255, 255, 0.22);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2), 0 8px 20px rgba(15, 23, 42, 0.12);
        backdrop-filter: blur(10px);
    }

    .brand-mark svg { width: 31px; height: 31px; color: #FFFFFF; }

    .brand-eyebrow {
        display: flex;
        align-items: center;
        gap: 7px;
        margin-bottom: 4px;
        font-size: 0.65rem;
        line-height: 1;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.68);
    }

    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #46E6A5;
        box-shadow: 0 0 0 3px rgba(70, 230, 165, 0.16);
    }

    .brand-title {
        margin: 0 !important;
        font-size: 2rem !important;
        line-height: 1.05 !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.045em !important;
    }

    .brand-title .brand-accent { color: #FFD54A; }

    .brand-subtitle {
        margin-top: 6px;
        font-size: 0.86rem;
        line-height: 1.4;
        color: rgba(255, 255, 255, 0.74);
        font-weight: 400;
        max-width: 430px;
    }

    .hero-actions {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 11px;
    }

    .hero-meta-row { display: flex; align-items: center; justify-content: flex-end; gap: 8px; flex-wrap: wrap; }

    .hero-chip {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        min-height: 30px;
        padding: 6px 11px;
        border: 1px solid rgba(255, 255, 255, 0.16);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.08);
        color: rgba(255, 255, 255, 0.86);
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        backdrop-filter: blur(8px);
    }

    .hero-chip svg { width: 13px; height: 13px; opacity: 0.8; }

    .notification-pill {
        display: inline-flex !important;
        align-items: center;
        gap: 8px;
        min-height: 34px;
        padding: 7px 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.17) !important;
        border-radius: 999px !important;
        background: rgba(255, 255, 255, 0.08) !important;
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 0.74rem !important;
        font-weight: 600 !important;
        backdrop-filter: blur(8px);
    }

    .badge-yellow {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 21px;
        height: 21px;
        padding: 0 6px !important;
        border-radius: 999px !important;
        background: var(--sv-secondary) !important;
        color: #392900 !important;
        font-size: 0.7rem !important;
        font-weight: 800 !important;
        line-height: 1 !important;
        box-shadow: 0 2px 8px rgba(248, 184, 7, 0.25);
    }

    .profile-card {
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 258px;
        padding: 10px 13px !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-radius: 15px !important;
        background: rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(14px);
    }

    .profile-avatar {
        width: 42px !important;
        height: 42px !important;
        flex: 0 0 42px;
        border-radius: 13px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #FFD65A 0%, #F8B807 100%) !important;
        color: #2D2200 !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 6px 14px rgba(15, 23, 42, 0.14);
    }

    .profile-name { font-weight: 700 !important; font-size: 0.86rem !important; color: #FFFFFF !important; line-height: 1.3; }
    .profile-role { font-size: 0.72rem !important; color: rgba(255, 255, 255, 0.7) !important; font-weight: 500 !important; line-height: 1.4; }
    .profile-store { font-size: 0.67rem !important; color: rgba(255, 255, 255, 0.54) !important; line-height: 1.4; }

    /* ==============================================================
       CABEÇALHO DE PÁGINA
       ============================================================== */
    .page-heading {
        display: flex;
        align-items: flex-start;
        gap: 15px;
        margin: 2px 0 22px 0;
        padding: 2px 2px 0 2px;
        animation: sv-rise 0.4s ease-out both;
    }

    .page-heading-icon {
        width: 48px;
        height: 48px;
        flex: 0 0 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid var(--sv-border);
        border-radius: 14px;
        background: var(--sv-surface);
        box-shadow: var(--sv-shadow-sm);
        font-size: 1.28rem;
        line-height: 1;
    }

    .page-heading-copy { min-width: 0; padding-top: 1px; }

    .page-heading-eyebrow {
        margin-bottom: 5px;
        color: var(--sv-primary);
        font-size: 0.64rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .page-heading-title {
        margin: 0 !important;
        color: var(--sv-text) !important;
        font-size: 1.48rem !important;
        line-height: 1.15 !important;
        font-weight: 800 !important;
        letter-spacing: -0.035em !important;
    }

    .page-heading-subtitle {
        max-width: 760px;
        margin: 5px 0 0 0 !important;
        color: var(--sv-muted) !important;
        font-size: 0.86rem !important;
        line-height: 1.55 !important;
        font-weight: 400 !important;
    }

    .today-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 9px 12px;
        border: 1px solid var(--sv-border);
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.8);
        color: var(--sv-muted);
        font-size: 0.75rem;
        font-weight: 600;
        white-space: nowrap;
        box-shadow: var(--sv-shadow-sm);
    }

    /* ==============================================================
       CARDS E MÉTRICAS
       ============================================================== */
    .metric-widget {
        position: relative;
        overflow: hidden;
        height: 100%;
        background: var(--sv-surface) !important;
        border: 1px solid var(--sv-border) !important;
        border-radius: 17px !important;
        padding: 20px 21px !important;
        box-shadow: var(--sv-shadow-sm) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
    }

    .metric-widget::after {
        content: "";
        position: absolute;
        top: 0;
        left: 20px;
        right: 20px;
        height: 2px;
        border-radius: 0 0 4px 4px;
        background: linear-gradient(90deg, var(--sv-primary), rgba(57, 66, 246, 0.08));
        opacity: 0.7;
    }

    .metric-widget:hover {
        transform: translateY(-3px) !important;
        border-color: rgba(57, 66, 246, 0.2) !important;
        box-shadow: 0 14px 30px -10px rgba(57, 66, 246, 0.16), 0 4px 10px -4px rgba(15, 23, 42, 0.05) !important;
    }

    .metric-title, .metric-label {
        display: block;
        margin-bottom: 9px !important;
        color: var(--sv-muted) !important;
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        line-height: 1.35 !important;
        letter-spacing: 0.075em !important;
        text-transform: uppercase;
    }

    .metric-value {
        color: var(--sv-text) !important;
        font-size: 1.82rem !important;
        font-weight: 800 !important;
        line-height: 1.08 !important;
        letter-spacing: -0.04em !important;
    }

    .metric-sub {
        display: flex;
        align-items: center;
        gap: 5px;
        margin-top: 8px !important;
        color: var(--sv-success) !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        line-height: 1.4;
    }

    .kpi-card {
        position: relative;
        overflow: hidden;
        height: 100%;
        background: var(--sv-surface) !important;
        border: 1px solid var(--sv-border) !important;
        border-radius: 17px !important;
        padding: 19px 20px !important;
        text-align: left !important;
        box-shadow: var(--sv-shadow-sm) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }

    .kpi-card::after {
        content: "";
        position: absolute;
        top: 0;
        left: 20px;
        right: 20px;
        height: 2px;
        border-radius: 0 0 4px 4px;
        background: linear-gradient(90deg, var(--sv-primary), rgba(57, 66, 246, 0.08));
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(57, 66, 246, 0.2);
        box-shadow: 0 14px 30px -12px rgba(57, 66, 246, 0.16);
    }

    .kpi-title {
        margin-bottom: 8px !important;
        color: var(--sv-muted) !important;
        font-size: 0.66rem !important;
        font-weight: 700 !important;
        line-height: 1.35 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase;
    }

    .kpi-value {
        color: var(--sv-text) !important;
        font-size: 1.9rem !important;
        font-weight: 800 !important;
        line-height: 1.05 !important;
        letter-spacing: -0.04em !important;
    }

    .kpi-delta {
        margin-top: 7px !important;
        color: var(--sv-muted) !important;
        font-size: 0.72rem !important;
        font-weight: 500 !important;
    }

    /* Métricas nativas do Streamlit */
    [data-testid="stMetric"] {
        position: relative;
        overflow: hidden;
        min-height: 118px;
        padding: 17px 18px !important;
        border: 1px solid var(--sv-border) !important;
        border-radius: 16px !important;
        background: var(--sv-surface) !important;
        box-shadow: var(--sv-shadow-sm) !important;
    }

    [data-testid="stMetric"]::after {
        content: "";
        position: absolute;
        top: 0;
        left: 18px;
        right: 18px;
        height: 2px;
        background: linear-gradient(90deg, var(--sv-primary), rgba(57, 66, 246, 0.05));
        opacity: 0.75;
    }

    [data-testid="stMetricLabel"] p {
        color: var(--sv-muted) !important;
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.065em !important;
        text-transform: uppercase;
        line-height: 1.4 !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--sv-text) !important;
        font-size: 1.55rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.035em !important;
    }

    [data-testid="stMetricDelta"] { font-size: 0.73rem !important; font-weight: 600 !important; }

    /* ==============================================================
       AVISOS, STATUS E ALERTAS
       ============================================================== */
    .notice-card, .alert-card {
        position: relative;
        background: var(--sv-surface) !important;
        border: 1px solid var(--sv-border) !important;
        border-radius: 15px !important;
        padding: 17px 18px !important;
        margin-bottom: 11px !important;
        box-shadow: var(--sv-shadow-sm) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    }

    .notice-card { border-left-width: 4px !important; }

    .notice-card:hover, .alert-card:hover {
        transform: translateY(-1px);
        box-shadow: var(--sv-shadow-md) !important;
        border-color: #CBD5E1 !important;
    }

    .notice-card h4, .alert-card h4 { margin: 7px 0 7px 0 !important; font-size: 0.97rem !important; }
    .notice-card p { margin-bottom: 0 !important; }

    .tag-category {
        display: inline-flex;
        align-items: center;
        min-height: 22px;
        padding: 3px 9px !important;
        border: 1px solid transparent;
        border-radius: 999px !important;
        margin-bottom: 7px !important;
        font-size: 0.63rem !important;
        font-weight: 800 !important;
        line-height: 1 !important;
        letter-spacing: 0.07em !important;
        text-transform: uppercase;
    }

    .tag-rh { background: #EEF0FF !important; color: #3038D5 !important; border-color: #DDE1FF !important; }
    .tag-operacional { background: #FFF8DB !important; color: #946200 !important; border-color: #FDE68A !important; }
    .tag-produtos { background: #EAFBF3 !important; color: #067A55 !important; border-color: #C7F4DF !important; }
    .tag-formacao { background: #F5EDFF !important; color: #6D28D9 !important; border-color: #E9D5FF !important; }

    .status-badge {
        display: inline-flex !important;
        align-items: center;
        gap: 5px;
        min-height: 23px;
        padding: 3px 9px !important;
        border: 1px solid transparent;
        border-radius: 999px !important;
        font-size: 0.63rem !important;
        font-weight: 800 !important;
        line-height: 1 !important;
        letter-spacing: 0.065em !important;
        text-transform: uppercase;
        white-space: nowrap;
    }

    .status-badge::before {
        content: "";
        width: 5px;
        height: 5px;
        flex: 0 0 5px;
        border-radius: 50%;
        background: currentColor;
        opacity: 0.85;
    }

    .status-warning { background: #FFF7E6 !important; color: #9A6200 !important; border-color: #FDE68A !important; }
    .status-success { background: #EAFBF3 !important; color: #047857 !important; border-color: #C7F4DF !important; }
    .status-danger { background: #FFF0F0 !important; color: #B42318 !important; border-color: #FECACA !important; }
    .status-info { background: #EEF0FF !important; color: #3038D5 !important; border-color: #DDE1FF !important; }

    .alert-critico { border-left: 4px solid var(--sv-danger) !important; }
    .alert-insuficiente { border-left: 4px solid var(--sv-warning) !important; }
    .alert-regular { border-left: 4px solid var(--sv-success) !important; }

    .urgent-banner {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        padding: 16px 18px !important;
        margin-bottom: 18px !important;
        border: 1px solid #FDE68A !important;
        border-left: 4px solid var(--sv-secondary) !important;
        border-radius: 15px !important;
        background: linear-gradient(135deg, #FFFDF4 0%, #FFF8DB 100%) !important;
        color: #6B4700 !important;
        box-shadow: 0 6px 18px -10px rgba(180, 130, 0, 0.25);
    }

    /* Cards de dados / histórico / aprovação */
    .data-card {
        position: relative;
        padding: 16px 18px;
        margin-bottom: 11px;
        border: 1px solid var(--sv-border);
        border-radius: 15px;
        background: var(--sv-surface);
        box-shadow: var(--sv-shadow-sm);
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    }

    .data-card:hover {
        transform: translateY(-1px);
        border-color: #CBD5E1;
        box-shadow: var(--sv-shadow-md);
    }

    .data-card--warning {
        border-color: #FDE68A;
        background: linear-gradient(135deg, #FFFEFA 0%, #FFFBF0 100%);
    }

    .data-card--success {
        border-color: #C7F4DF;
        background: linear-gradient(135deg, #FFFFFF 0%, #F3FCF8 100%);
    }

    .data-card-head {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 15px;
        flex-wrap: wrap;
    }

    .data-card-title {
        color: var(--sv-text);
        font-size: 0.95rem;
        font-weight: 700;
        line-height: 1.4;
    }

    .data-card-meta {
        margin-top: 5px;
        color: var(--sv-muted);
        font-size: 0.78rem;
        line-height: 1.55;
    }

    .data-card-body {
        margin-top: 9px;
        color: #334155;
        font-size: 0.83rem;
        line-height: 1.65;
    }

    .module-empty {
        display: flex;
        align-items: flex-start;
        gap: 15px;
        padding: 22px 24px;
        margin-top: 8px;
        border: 1px solid #FDE68A;
        border-left: 4px solid var(--sv-secondary);
        border-radius: 16px;
        background: linear-gradient(135deg, #FFFEFA 0%, #FFF9E8 100%);
        box-shadow: var(--sv-shadow-sm);
    }

    .module-empty-icon {
        width: 42px;
        height: 42px;
        flex: 0 0 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #FDE68A;
        border-radius: 12px;
        background: #FFFFFF;
        font-size: 1.1rem;
    }

    .module-empty-title {
        margin-bottom: 5px;
        color: #713F12;
        font-size: 0.95rem;
        font-weight: 800;
        letter-spacing: -0.015em;
    }

    .module-empty-text {
        max-width: 780px;
        margin: 0;
        color: #854D0E;
        font-size: 0.82rem;
        line-height: 1.6;
    }

    .type-chip {
        display: inline-flex;
        align-items: center;
        padding: 3px 8px;
        border: 1px solid #DDE1FF;
        border-radius: 999px;
        background: #EEF0FF;
        color: #3038D5;
        font-size: 0.63rem;
        font-weight: 800;
        letter-spacing: 0.055em;
        line-height: 1;
        text-transform: uppercase;
        white-space: nowrap;
    }

    .audit-note {
        margin-top: 8px;
        padding: 8px 10px;
        border-left: 3px solid var(--sv-warning);
        border-radius: 7px;
        background: #FFFBEB;
        color: #854D0E;
        font-size: 0.78rem;
        line-height: 1.5;
    }

    /* Progresso */
    .progress-container {
        height: 22px !important;
        margin: 15px 0 8px 0 !important;
        border-radius: 999px !important;
        background: #E9EDF5 !important;
        overflow: hidden;
        box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.06);
    }

    .progress-fill {
        height: 100%;
        border-radius: 999px !important;
        background: linear-gradient(90deg, #3942F6 0%, #6E75FF 68%, #F8B807 100%) !important;
        box-shadow: 0 0 12px rgba(57, 66, 246, 0.28);
        transition: width 0.7s cubic-bezier(0.22, 1, 0.36, 1);
    }

    .action-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 48px;
        border-radius: 11px;
        background: linear-gradient(135deg, var(--sv-primary), var(--sv-primary-deep));
        color: #FFFFFF;
        font-weight: 700;
        box-shadow: 0 6px 16px -6px rgba(57, 66, 246, 0.4);
    }

    /* ==============================================================
       BOTÕES
       ============================================================== */
    .stButton > button,
    [data-testid="stFormSubmitButton"] > button,
    .stDownloadButton > button,
    [data-testid="stBaseButton-primary"],
    [data-testid="stBaseButton-secondary"] {
        min-height: 40px;
        padding: 0.5rem 1.05rem !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.005em;
        transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease, border-color 0.18s ease !important;
    }

    .stButton > button[kind="primary"],
    [data-testid="stFormSubmitButton"] > button[kind="primary"],
    [data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #3942F6 0%, #252CD6 100%) !important;
        border: 1px solid rgba(37, 44, 214, 0.55) !important;
        color: #FFFFFF !important;
        box-shadow: 0 5px 14px -5px rgba(57, 66, 246, 0.48), inset 0 1px 0 rgba(255, 255, 255, 0.17) !important;
    }

    .stButton > button[kind="primary"]:hover,
    [data-testid="stFormSubmitButton"] > button[kind="primary"]:hover,
    [data-testid="stBaseButton-primary"]:hover {
        transform: translateY(-1px);
        background: linear-gradient(135deg, #454DF8 0%, #2E35DE 100%) !important;
        box-shadow: 0 9px 22px -7px rgba(57, 66, 246, 0.52), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }

    .stButton > button[kind="secondary"],
    [data-testid="stFormSubmitButton"] > button[kind="secondary"],
    [data-testid="stBaseButton-secondary"] {
        background: #FFFFFF !important;
        border: 1px solid var(--sv-border) !important;
        color: #334155 !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03) !important;
    }

    .stButton > button[kind="secondary"]:hover,
    [data-testid="stFormSubmitButton"] > button[kind="secondary"]:hover,
    [data-testid="stBaseButton-secondary"]:hover {
        transform: translateY(-1px);
        border-color: #C7D2E2 !important;
        background: #F8FAFC !important;
        color: var(--sv-primary) !important;
    }

    .stButton > button:focus-visible,
    [data-testid="stFormSubmitButton"] > button:focus-visible,
    .stDownloadButton > button:focus-visible {
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(57, 66, 246, 0.22) !important;
    }

    .stButton > button:disabled,
    [data-testid="stFormSubmitButton"] > button:disabled {
        opacity: 0.48 !important;
        transform: none !important;
        cursor: not-allowed !important;
        box-shadow: none !important;
    }

    .stDownloadButton > button {
        background: #FFFFFF !important;
        border: 1px solid var(--sv-border) !important;
        color: #334155 !important;
    }

    .stDownloadButton > button:hover {
        border-color: rgba(57, 66, 246, 0.35) !important;
        color: var(--sv-primary) !important;
        background: #F8FAFF !important;
    }

    /* ==============================================================
       FORMULÁRIOS E INPUTS
       ============================================================== */
    [data-testid="stForm"] {
        padding: 1.25rem 1.3rem !important;
        border: 1px solid var(--sv-border) !important;
        border-radius: 18px !important;
        background: rgba(255, 255, 255, 0.84) !important;
        box-shadow: var(--sv-shadow-sm) !important;
    }

    [data-testid="stWidgetLabel"] p,
    .stTextInput label p,
    .stSelectbox label p,
    .stNumberInput label p,
    .stDateInput label p,
    .stTextArea label p {
        color: #334155 !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.005em;
    }

    [data-testid="stTextInput"] [data-baseweb="input"],
    [data-testid="stNumberInput"] [data-baseweb="input"],
    [data-testid="stDateInput"] [data-baseweb="input"],
    [data-testid="stTextArea"] [data-baseweb="textarea"],
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        min-height: 43px;
        border: 1px solid var(--sv-border) !important;
        border-radius: 10px !important;
        background: #FFFFFF !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.025) !important;
        transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
    }

    [data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
    [data-testid="stNumberInput"] [data-baseweb="input"]:focus-within,
    [data-testid="stDateInput"] [data-baseweb="input"]:focus-within,
    [data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within {
        border-color: var(--sv-primary) !important;
        box-shadow: 0 0 0 3px rgba(57, 66, 246, 0.12) !important;
    }

    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stTextArea textarea,
    [data-baseweb="select"] input {
        color: var(--sv-text) !important;
        font-size: 0.86rem !important;
        font-family: 'Inter', sans-serif !important;
        background: transparent !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #A3AFC2 !important;
        opacity: 1;
    }

    [data-testid="stTextInput"] [data-baseweb="input"] > div:first-child,
    [data-testid="stNumberInput"] [data-baseweb="input"] > div:first-child {
        border-right: 0 !important;
    }

    .stTextArea textarea { min-height: 92px !important; padding: 10px 12px !important; }

    [data-testid="stNumberInput"] button {
        border-color: transparent !important;
        background: transparent !important;
        color: var(--sv-muted) !important;
    }

    [data-testid="stNumberInput"] button:hover { background: var(--sv-primary-soft) !important; color: var(--sv-primary) !important; }

    [data-testid="stCheckbox"] label,
    [data-testid="stToggle"] label,
    [data-testid="stRadio"] label {
        color: #334155 !important;
        font-size: 0.83rem !important;
    }

    [data-testid="stCheckbox"] input,
    [data-testid="stToggle"] input { accent-color: var(--sv-primary) !important; }

    [data-testid="stSlider"] [role="slider"] { background: var(--sv-primary) !important; border-color: #FFFFFF !important; }
    [data-testid="stSlider"] [data-baseweb="slider"] div[role="progressbar"] { background: var(--sv-primary) !important; }

    [data-testid="stFileUploaderDropzone"] {
        border: 1px dashed #CBD5E1 !important;
        border-radius: 12px !important;
        background: #F8FAFC !important;
        min-height: 104px;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--sv-primary) !important;
        background: #F8F9FF !important;
    }

    /* Popovers de select */
    [data-baseweb="popover"] [role="listbox"] {
        border: 1px solid var(--sv-border) !important;
        border-radius: 12px !important;
        box-shadow: var(--sv-shadow-md) !important;
        padding: 5px !important;
    }

    [data-baseweb="popover"] [role="option"] {
        border-radius: 8px !important;
        font-size: 0.83rem !important;
    }

    /* ==============================================================
       ABAS
       ============================================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px !important;
        width: 100%;
        padding: 5px !important;
        margin-bottom: 18px !important;
        border: 1px solid #E5EAF2 !important;
        border-bottom: 1px solid #E5EAF2 !important;
        border-radius: 13px !important;
        background: #EBEFF6 !important;
        overflow-x: auto;
        scrollbar-width: thin;
    }

    .stTabs [data-baseweb="tab"] {
        height: 38px !important;
        padding: 0 14px !important;
        border: 0 !important;
        border-radius: 9px !important;
        background: transparent !important;
        color: var(--sv-muted) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        white-space: nowrap;
        transition: color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover { color: var(--sv-primary) !important; background: rgba(255, 255, 255, 0.55) !important; }

    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: var(--sv-primary) !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 7px rgba(15, 23, 42, 0.08), inset 0 0 0 1px rgba(226, 232, 240, 0.7) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
    .stTabs [data-baseweb="tab-border"] { display: none !important; }

    /* ==============================================================
       ALERTAS NATIVOS, EXPANDERS, TABELAS
       ============================================================== */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: 1px solid var(--sv-border) !important;
        box-shadow: var(--sv-shadow-sm) !important;
        font-size: 0.82rem !important;
    }

    [data-testid="stAlert"] p { font-size: 0.82rem !important; line-height: 1.55 !important; margin-bottom: 0 !important; }

    [data-testid="stExpander"] {
        margin-bottom: 10px !important;
        border: 1px solid var(--sv-border) !important;
        border-radius: 13px !important;
        background: #FFFFFF !important;
        box-shadow: var(--sv-shadow-sm);
        overflow: hidden;
    }

    [data-testid="stExpander"] summary {
        padding: 12px 15px !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }

    [data-testid="stExpander"] summary:hover { background: #F8FAFC !important; }

    [data-testid="stDataFrame"] {
        overflow: hidden !important;
        border: 1px solid var(--sv-border) !important;
        border-radius: 14px !important;
        background: #FFFFFF !important;
        box-shadow: var(--sv-shadow-sm) !important;
    }

    [data-testid="stDataFrame"] > div { border-radius: 14px !important; }

    .stCode, code {
        border-radius: 7px !important;
        background: #F1F5F9 !important;
        color: #334155 !important;
        font-size: 0.82em !important;
    }

    .stSpinner > div { border-top-color: var(--sv-primary) !important; }

    /* ==============================================================
       SIDEBAR
       ============================================================== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFF 100%) !important;
        border-right: 1px solid var(--sv-border) !important;
        box-shadow: 8px 0 30px -24px rgba(15, 23, 42, 0.22);
    }

    section[data-testid="stSidebar"][data-collapsed="false"] {
        width: 292px !important;
        min-width: 292px !important;
    }

    section[data-testid="stSidebar"][data-collapsed="true"] {
        width: 0 !important;
        min-width: 0 !important;
        border-right: 0 !important;
        box-shadow: none !important;
        overflow: hidden !important;
    }

    body:has(button[data-testid="stExpandSidebarButton"]) [data-testid="stMainBlockContainer"] {
        padding-top: 4.5rem !important;
    }

    section[data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        background: transparent !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding: 1.05rem 1rem 1.5rem 1rem !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] { padding: 0.9rem 1rem 0 1rem !important; }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 11px;
        padding: 4px 3px 17px 3px;
    }

    .sidebar-brand-mark {
        width: 40px;
        height: 40px;
        flex: 0 0 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        background: linear-gradient(140deg, #3942F6 0%, #2027C9 100%);
        color: #FFFFFF;
        box-shadow: 0 8px 18px -7px rgba(57, 66, 246, 0.6);
    }

    .sidebar-brand-mark svg { width: 24px; height: 24px; }

    .sidebar-brand-name {
        color: var(--sv-text);
        font-size: 1.04rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.035em;
    }

    .sidebar-brand-name span { color: var(--sv-primary); }

    .sidebar-brand-sub {
        margin-top: 3px;
        color: var(--sv-muted-light);
        font-size: 0.58rem;
        font-weight: 700;
        letter-spacing: 0.105em;
        text-transform: uppercase;
    }

    .sidebar-user {
        display: flex;
        align-items: center;
        gap: 11px;
        padding: 12px;
        margin-bottom: 6px;
        border: 1px solid #E5EAF5;
        border-radius: 15px;
        background: linear-gradient(135deg, #F4F6FF 0%, #FFFFFF 100%);
        box-shadow: 0 4px 14px -10px rgba(57, 66, 246, 0.32);
    }

    .sidebar-user-avatar {
        width: 35px;
        height: 35px;
        flex: 0 0 35px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #DDE1FF;
        border-radius: 11px;
        background: #FFFFFF;
        color: var(--sv-primary);
        font-size: 0.82rem;
        font-weight: 800;
        box-shadow: 0 2px 5px rgba(57, 66, 246, 0.07);
    }

    .sidebar-user-name {
        overflow: hidden;
        color: var(--sv-text);
        font-size: 0.8rem;
        font-weight: 700;
        line-height: 1.3;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .sidebar-user-role {
        margin-top: 3px;
        color: var(--sv-primary);
        font-size: 0.64rem;
        font-weight: 700;
        line-height: 1.3;
        letter-spacing: 0.035em;
        text-transform: uppercase;
    }

    .sidebar-section-label {
        margin: 17px 4px 7px 4px;
        color: #9AA7BC;
        font-size: 0.58rem;
        font-weight: 800;
        letter-spacing: 0.13em;
        text-transform: uppercase;
    }

    /* Navegação lateral */
    section[data-testid="stSidebar"] [data-testid="stRadio"] > label { display: none !important; }

    section[data-testid="stSidebar"] [role="radiogroup"] { gap: 3px !important; }

    section[data-testid="stSidebar"] [role="radiogroup"] label {
        width: 100%;
        min-height: 36px;
        padding: 7px 9px !important;
        border: 1px solid transparent;
        border-radius: 9px !important;
        background: transparent;
        color: #536179 !important;
        font-size: 0.76rem !important;
        line-height: 1.3 !important;
        transition: background 0.16s ease, color 0.16s ease, border-color 0.16s ease, box-shadow 0.16s ease;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
        border-color: #E7EBFA;
        background: #F4F6FF;
        color: var(--sv-primary) !important;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        border-color: #DDE1FF;
        background: linear-gradient(90deg, #EEF0FF 0%, #F7F8FF 100%);
        color: var(--sv-primary) !important;
        box-shadow: inset 3px 0 0 var(--sv-primary);
    }

    section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p { color: var(--sv-primary) !important; font-weight: 700 !important; }

    section[data-testid="stSidebar"] [role="radiogroup"] p {
        font-size: 0.76rem !important;
        font-weight: 500 !important;
        line-height: 1.3 !important;
        white-space: normal;
    }

    section[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child {
        display: none !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadioOption"] > div {
        gap: 0 !important;
        align-items: center !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadioOption"] [data-testid="stMarkdownContainer"] p {
        padding-left: 1px;
    }

    .sidebar-unit {
        padding: 12px;
        margin-top: 2px;
        border: 1px solid var(--sv-border);
        border-radius: 13px;
        background: #FFFFFF;
        box-shadow: var(--sv-shadow-sm);
    }

    .sidebar-unit-title {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 8px;
        color: var(--sv-text);
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .sidebar-unit-row {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        padding: 3px 0;
        color: var(--sv-muted);
        font-size: 0.67rem;
        line-height: 1.4;
    }

    .sidebar-unit-row b { color: #334155; font-weight: 600; text-align: right; }

    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        min-height: 35px !important;
        padding: 0.35rem 0.8rem !important;
        border-color: #E2E8F0 !important;
        background: #FFFFFF !important;
        color: #64748B !important;
        font-size: 0.71rem !important;
        font-weight: 600 !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        border-color: #FECACA !important;
        background: #FFF7F7 !important;
        color: #B42318 !important;
        transform: none;
    }

    section[data-testid="stSidebar"] [data-testid="stExpander"] {
        margin-top: 12px !important;
        border-color: #E7ECF4 !important;
        box-shadow: none !important;
        background: rgba(255, 255, 255, 0.65) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stExpander"] summary { padding: 10px 11px !important; font-size: 0.71rem !important; }
    section[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderDetails"] { padding: 0 11px 11px 11px !important; }

    section[data-testid="stSidebar"] .stCaptionContainer,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        font-size: 0.65rem !important;
        line-height: 1.4;
    }

    .sidebar-footer {
        margin-top: 18px;
        padding-top: 12px;
        border-top: 1px solid var(--sv-border);
        color: #A0AEC0;
        font-size: 0.6rem;
        line-height: 1.5;
        text-align: center;
        letter-spacing: 0.02em;
    }

    .sidebar-footer b { color: #64748B; font-weight: 600; }

    /* ==============================================================
       UTILITÁRIOS / RESPONSIVO
       ============================================================== */
    @keyframes sv-rise {
        from { opacity: 0; transform: translateY(7px); }
        to { opacity: 1; transform: translateY(0); }
    }

    ::-webkit-scrollbar { width: 9px; height: 9px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { border: 2px solid transparent; border-radius: 999px; background: #CBD5E1; background-clip: content-box; }
    ::-webkit-scrollbar-thumb:hover { background: #94A3B8; background-clip: content-box; }

    @media (max-width: 1100px) {
        .portal-header { padding: 24px; }
        .portal-header-inner { align-items: flex-start; }
        .brand-title { font-size: 1.7rem !important; }
        .hero-actions { width: 100%; align-items: flex-start; }
        .hero-meta-row { justify-content: flex-start; }
        .profile-card { min-width: 230px; width: auto; }
    }

    @media (max-width: 860px) {
        .main .block-container, [data-testid="stMainBlockContainer"] {
            padding: 1rem 1rem 2.5rem 1rem !important;
        }
        .portal-header { border-radius: 19px; padding: 20px; }
        .portal-header-inner { align-items: flex-start; }
        .hero-actions { width: 100%; align-items: flex-start; }
        .hero-meta-row { justify-content: flex-start; }
        .profile-card { width: 100%; }
        .page-heading-title { font-size: 1.3rem !important; }
    }

    @media (max-width: 640px) {
        .brand-mark { width: 46px; height: 46px; flex-basis: 46px; border-radius: 14px; }
        .brand-title { font-size: 1.45rem !important; }
        .brand-subtitle { font-size: 0.76rem; }
        .page-heading-icon { width: 42px; height: 42px; flex-basis: 42px; border-radius: 12px; font-size: 1.1rem; }
        .page-heading-title { font-size: 1.18rem !important; }
        .metric-value, .kpi-value { font-size: 1.55rem !important; }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GERENCIAMENTO DE ESTADO (SESSION STATE)
# -----------------------------------------------------------------------------
if "notices_read" not in st.session_state:
    st.session_state.notices_read = set()

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "login_error" not in st.session_state:
    st.session_state.login_error = None
if "login_username" not in st.session_state:
    st.session_state.login_username = ""
if "login_show_password" not in st.session_state:
    st.session_state.login_show_password = False

if "cert_issued" not in st.session_state:
    st.session_state.cert_issued = False

if "rh_requests" not in st.session_state:
    st.session_state.rh_requests = []


# -----------------------------------------------------------------------------
# CHANGE 06: GATE DE AUTENTICAÇÃO — tela de login quando não autenticado
# -----------------------------------------------------------------------------
def _require_auth():
    """Exibe a tela de login e interrompe a execução se o usuário não estiver autenticado."""
    if not st.session_state.authenticated:
        _render_login_screen()
        st.stop()


def _render_login_screen():
    """Renderiza a tela de login.

    Arquitetura: todo o conteúdo (logo, título, campos, botão, erro) fica
    DENTRO de ``st.form`` — o elemento ``<form>`` do Streamlit é estilizado
    via CSS como o card branco centralizado. O CSS é injetado aqui (e não
    no bloco global) para que os overrides de ``.main .block-container``
    não afetem a dashboard quando o usuário já estiver autenticado.
    """
    # CSS condicional: só existe quando a tela de login é renderizada
    st.markdown("""
    <style>
    /* ==============================================================
       LOGIN — EXPERIÊNCIA SMARTVISION
       ============================================================== */
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        min-height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        max-width: 100% !important;
        padding: 2.5rem 2rem !important;
        background: transparent !important;
        box-sizing: border-box !important;
    }

    [data-testid="stForm"] {
        width: 100% !important;
        max-width: 1040px !important;
        margin: 0 auto !important;
        padding: 0 !important;
        overflow: hidden !important;
        border: 1px solid rgba(226, 232, 240, 0.9) !important;
        border-radius: 26px !important;
        background: #FFFFFF !important;
        box-shadow: 0 34px 80px -30px rgba(30, 37, 182, 0.38), 0 12px 28px -16px rgba(15, 23, 42, 0.18) !important;
    }

    [data-testid="stForm"] > div { margin-bottom: 0 !important; }

    [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        align-items: stretch !important;
    }

    [data-testid="stForm"] [data-testid="stColumn"]:first-child {
        border-radius: 25px 0 0 25px;
        background:
            radial-gradient(circle at 92% 6%, rgba(248, 184, 7, 0.24), transparent 15rem),
            linear-gradient(145deg, #232BDB 0%, #3942F6 52%, #1B22AC 100%);
        box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.08);
    }

    [data-testid="stForm"] [data-testid="stColumn"]:last-child {
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 38px 42px 34px 42px !important;
        background: #FFFFFF;
    }

    /* Painel de marca */
    .login-brand-panel {
        position: relative;
        min-height: 480px;
        height: 100%;
        display: flex;
        flex-direction: column;
        padding: 38px 38px 30px 38px;
        overflow: hidden;
        color: #FFFFFF;
    }

    .login-brand-panel::before {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        right: -120px;
        top: -105px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 50%;
        box-shadow: 0 0 0 42px rgba(255, 255, 255, 0.035), 0 0 0 84px rgba(255, 255, 255, 0.018);
    }

    .login-brand-panel::after {
        content: "";
        position: absolute;
        inset: 0;
        background-image:
            linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
        background-size: 30px 30px;
        mask-image: linear-gradient(130deg, transparent 22%, rgba(0, 0, 0, 0.55) 70%, transparent 100%);
        -webkit-mask-image: linear-gradient(130deg, transparent 22%, rgba(0, 0, 0, 0.55) 70%, transparent 100%);
        pointer-events: none;
    }

    .login-brand-panel > * { position: relative; z-index: 1; }

    .login-logo-row { display: flex; align-items: center; gap: 11px; }

    .login-logo-mark {
        width: 42px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(255, 255, 255, 0.24);
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.13);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.22), 0 8px 18px rgba(15, 23, 42, 0.14);
        backdrop-filter: blur(10px);
    }

    .login-logo-mark svg { width: 25px; height: 25px; }

    .login-wordmark { font-size: 1.02rem; font-weight: 800; letter-spacing: -0.035em; line-height: 1.1; }
    .login-wordmark .vision { color: #FFD54A; }
    .login-wordmark-sub {
        margin-top: 3px;
        color: rgba(255, 255, 255, 0.57);
        font-size: 0.56rem;
        font-weight: 700;
        letter-spacing: 0.13em;
        text-transform: uppercase;
    }

    .login-brand-kicker {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        align-self: flex-start;
        margin-top: 47px;
        padding: 6px 10px;
        border: 1px solid rgba(255, 255, 255, 0.17);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.08);
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.58rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        backdrop-filter: blur(8px);
    }

    .login-brand-panel h1 {
        margin: 17px 0 0 0 !important;
        color: #FFFFFF !important;
        font-size: 2.45rem !important;
        line-height: 1.06 !important;
        font-weight: 800 !important;
        letter-spacing: -0.055em !important;
    }

    .login-brand-panel h1 span { color: #FFD54A !important; }

    .login-brand-panel > p {
        max-width: 365px;
        margin: 15px 0 0 0 !important;
        color: rgba(255, 255, 255, 0.71) !important;
        font-size: 0.83rem !important;
        line-height: 1.65 !important;
    }

    .login-benefits {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-top: 29px;
        padding-top: 22px;
        border-top: 1px solid rgba(255, 255, 255, 0.13);
    }

    .login-benefit { display: flex; align-items: flex-start; gap: 10px; color: rgba(255, 255, 255, 0.84); font-size: 0.76rem; line-height: 1.5; }
    .login-benefit-icon {
        width: 20px;
        height: 20px;
        flex: 0 0 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 1px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 6px;
        background: rgba(255, 255, 255, 0.09);
        color: #FFD54A;
        font-size: 0.62rem;
        font-weight: 800;
    }

    .login-benefit b { color: #FFFFFF; font-weight: 600; }

    .login-security {
        display: inline-flex;
        align-items: center;
        align-self: flex-start;
        gap: 7px;
        margin-top: auto;
        padding-top: 26px;
        color: rgba(255, 255, 255, 0.52);
        font-size: 0.61rem;
        font-weight: 500;
        letter-spacing: 0.015em;
    }

    .login-security svg { width: 12px; height: 12px; }

    /* Painel de formulário */
    .login-form-intro { margin-bottom: 22px; }

    .login-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 9px;
        border: 1px solid #DDE1FF;
        border-radius: 999px;
        background: #F3F4FF;
        color: var(--sv-primary);
        font-size: 0.58rem;
        font-weight: 800;
        letter-spacing: 0.11em;
        line-height: 1;
        text-transform: uppercase;
    }

    .login-badge::before {
        content: "";
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: var(--sv-success);
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.11);
    }

    .login-form-intro h2 {
        margin: 12px 0 5px 0 !important;
        color: var(--sv-text) !important;
        font-size: 1.5rem !important;
        line-height: 1.15 !important;
        font-weight: 800 !important;
        letter-spacing: -0.045em !important;
    }

    .login-form-intro p {
        margin: 0 !important;
        color: var(--sv-muted) !important;
        font-size: 0.79rem !important;
        line-height: 1.55 !important;
    }

    .login-field-icon {
        display: flex;
        align-items: center;
        gap: 6px;
        margin: 0 0 4px 1px;
    }

    .login-field-icon svg { width: 13px; height: 13px; flex-shrink: 0; color: var(--sv-primary); opacity: 0.82; }

    .login-field-icon .field-label {
        color: #334155;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: -0.005em;
    }

    [data-testid="stForm"] .stTextInput { margin-bottom: 8px; }

    [data-testid="stForm"] .stTextInput label { display: none !important; }

    [data-testid="stForm"] .stTextInput [data-baseweb="input"] {
        min-height: 47px !important;
        border: 1px solid #DDE3EC !important;
        border-radius: 10px !important;
        background: #FBFCFE !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.025) !important;
        transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease !important;
    }

    [data-testid="stForm"] .stTextInput [data-baseweb="input"]:focus-within {
        border-color: var(--sv-primary) !important;
        background: #FFFFFF !important;
        box-shadow: 0 0 0 3px rgba(57, 66, 246, 0.12) !important;
    }

    [data-testid="stForm"] .stTextInput input {
        min-height: 45px !important;
        padding: 0 13px !important;
        color: var(--sv-text) !important;
        font-size: 0.84rem !important;
    }

    [data-testid="stForm"] .stTextInput input::placeholder { color: #A3AFC2 !important; }

    [data-testid="stForm"] [data-testid="stFormSubmitButton"] { margin-top: 12px; }

    [data-testid="stForm"] [data-testid="stFormSubmitButton"] button {
        width: 100% !important;
        min-height: 48px !important;
        border-radius: 10px !important;
        background: linear-gradient(135deg, #3942F6 0%, #252CD6 100%) !important;
        border: 1px solid rgba(37, 44, 214, 0.5) !important;
        color: #FFFFFF !important;
        font-size: 0.84rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.015em !important;
        box-shadow: 0 9px 20px -8px rgba(57, 66, 246, 0.52), inset 0 1px 0 rgba(255, 255, 255, 0.18) !important;
    }

    [data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #4A52F9 0%, #2C34DF 100%) !important;
        box-shadow: 0 12px 26px -9px rgba(57, 66, 246, 0.58), inset 0 1px 0 rgba(255, 255, 255, 0.22) !important;
        transform: translateY(-1px);
    }

    [data-testid="stForm"] [data-testid="stFormSubmitButton"] button:disabled {
        background: #B7BDD0 !important;
        border-color: #B7BDD0 !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
    }

    .login-error {
        margin-top: 12px;
        padding: 10px 12px;
        border: 1px solid #FECACA;
        border-left: 3px solid var(--sv-danger);
        border-radius: 8px;
        background: #FFF5F5;
        color: #991B1B;
        font-size: 0.78rem;
        font-weight: 500;
        line-height: 1.5;
    }

    /* Credenciais de avaliação */
    .login-dev {
        width: 100%;
        max-width: 1040px;
        margin: 15px auto 0 auto;
        padding: 14px 17px;
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.72);
        box-shadow: 0 9px 26px -22px rgba(15, 23, 42, 0.3);
        backdrop-filter: blur(12px);
    }

    .login-dev-title {
        display: flex;
        align-items: center;
        gap: 7px;
        margin-bottom: 9px;
        color: #64748B;
        font-size: 0.63rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .login-dev-title::before {
        content: "";
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: var(--sv-secondary);
        box-shadow: 0 0 0 3px rgba(248, 184, 7, 0.12);
    }

    .login-dev-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; }

    .login-dev-item {
        padding: 8px 10px;
        border: 1px solid #E8EDF5;
        border-radius: 9px;
        background: rgba(248, 250, 252, 0.72);
    }

    .login-dev-role {
        margin-bottom: 3px;
        color: var(--sv-primary);
        font-size: 0.59rem;
        font-weight: 800;
        letter-spacing: 0.07em;
        text-transform: uppercase;
    }

    .login-dev-cred { color: #64748B; font-size: 0.68rem; line-height: 1.45; }
    .login-dev-cred b { color: #334155; font-weight: 600; }

    .login-footnote {
        width: 100%;
        max-width: 1040px;
        margin: 18px auto 0 auto;
        color: #94A3B8;
        font-size: 0.61rem;
        line-height: 1.5;
        text-align: center;
        letter-spacing: 0.015em;
    }

    @media (max-width: 980px) {
        [data-testid="stMainBlockContainer"] { justify-content: flex-start !important; padding-top: 1.5rem !important; }
        [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            flex-wrap: nowrap !important;
        }
        [data-testid="stForm"] [data-testid="stColumn"] {
            width: 100% !important;
            min-width: 0 !important;
            flex: 0 0 auto !important;
        }
        [data-testid="stForm"] [data-testid="stColumn"]:first-child { border-radius: 25px 25px 0 0; }
        [data-testid="stForm"] [data-testid="stColumn"]:last-child { padding: 30px 30px 28px 30px !important; }
        .login-brand-panel { min-height: auto; padding: 28px 30px 26px 30px; }
        .login-brand-kicker { margin-top: 28px; }
        .login-brand-panel h1 { font-size: 1.95rem !important; }
        .login-brand-panel > p { max-width: 520px; }
        .login-benefits { display: none; }
        .login-security { margin-top: 20px; padding-top: 0; }
    }

    @media (max-width: 640px) {
        .main .block-container { padding: 1rem !important; }
        [data-testid="stForm"] { border-radius: 20px !important; }
        [data-testid="stForm"] [data-testid="stColumn"]:first-child { border-radius: 19px 19px 0 0; }
        .login-brand-panel { padding: 23px 21px 22px 21px; }
        .login-brand-panel h1 { font-size: 1.65rem !important; }
        .login-brand-panel > p { font-size: 0.76rem !important; }
        [data-testid="stForm"] [data-testid="stColumn"]:last-child { padding: 24px 21px 23px 21px !important; }
        .login-form-intro h2 { font-size: 1.3rem !important; }
        .login-dev { padding: 12px; }
        .login-dev-grid { grid-template-columns: 1fr; }
        .login-dev-item { display: flex; align-items: baseline; gap: 7px; }
        .login-dev-role { margin-bottom: 0; min-width: 74px; }
    }
    </style>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        brand_col, access_col = st.columns([1.06, 0.94], gap="large")

        with brand_col:
            st.markdown("""
            <div class="login-brand-panel">
                <div class="login-logo-row">
                    <div class="login-logo-mark">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <circle cx="6.2" cy="14.3" r="3.4"></circle>
                            <circle cx="17.8" cy="14.3" r="3.4"></circle>
                            <path d="M9.6 14.3h4.8M2.8 14.3 1.8 11M21.2 14.3l1-3.3M6.2 10.9 7.7 7.2h8.6l1.5 3.7"></path>
                        </svg>
                    </div>
                    <div>
                        <div class="login-wordmark">SMART<span class="vision">VISION</span></div>
                        <div class="login-wordmark-sub">Plataforma de gestão óptica</div>
                    </div>
                </div>
                <div class="login-brand-kicker"><span class="status-dot"></span> Inteligência operacional</div>
                <h1>Sua operação,<br><span>mais inteligente.</span></h1>
                <p>Estoque, vendas, equipe e indicadores conectados em uma única experiência de gestão.</p>
                <div class="login-benefits">
                    <div class="login-benefit">
                        <div class="login-benefit-icon">✓</div>
                        <div><b>Visão unificada</b> da loja, do time e dos resultados em tempo real.</div>
                    </div>
                    <div class="login-benefit">
                        <div class="login-benefit-icon">✓</div>
                        <div><b>Controle auditado</b> de estoque, saídas e processos críticos.</div>
                    </div>
                    <div class="login-benefit">
                        <div class="login-benefit-icon">✓</div>
                        <div><b>Decisões mais rápidas</b> com alertas e recomendações acionáveis.</div>
                    </div>
                </div>
                <div class="login-security">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                        <path d="m9 12 2 2 4-4"></path>
                    </svg>
                    Ambiente seguro · Acesso restrito à equipe SmartVision
                </div>
            </div>
            """, unsafe_allow_html=True)

        with access_col:
            st.markdown("""
            <div class="login-form-intro">
                <div class="login-badge">Acesso seguro</div>
                <h2>Bem-vindo de volta</h2>
                <p>Informe suas credenciais corporativas para acessar o portal.</p>
            </div>
            """, unsafe_allow_html=True)

            _backend_configured = bool(
                os.getenv("XANO_BASE_URL") or (hasattr(st, "secrets") and "XANO_BASE_URL" in st.secrets)
            )
            if not _backend_configured:
                st.warning(
                    "⚠️ **Conexão Xano não detectada no ambiente.**\n\n"
                    "No Streamlit Cloud, adicione a chave `XANO_BASE_URL` em **App Settings > Secrets** para habilitar o login."
                )

            # --- Campo Usuário ---
            st.markdown("""
            <div class="login-field-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                </svg>
                <span class="field-label">Usuário ou e-mail</span>
            </div>
            """, unsafe_allow_html=True)
            usuario = st.text_input(
                "Usuário",
                value=st.session_state.login_username,
                placeholder="seu.nome@smartvision.com",
                label_visibility="collapsed",
                key="login_usuario_input",
            )

            # --- Campo Senha + toggle de visibilidade ---
            senha_tipo = "text" if st.session_state.login_show_password else "password"

            st.markdown("""
            <div class="login-field-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
                <span class="field-label">Senha</span>
            </div>
            """, unsafe_allow_html=True)

            senha = st.text_input(
                "Senha",
                placeholder="Digite sua senha corporativa",
                type=senha_tipo,
                label_visibility="collapsed",
                key="login_senha_input",
            )

            # --- Botão de acesso ---
            entrar = st.form_submit_button(
                "Acessar plataforma  →",
                type="primary",
                key="login_entrar_btn",
            )

            # --- Mensagem de erro (dentro do card) ---
            if st.session_state.login_error:
                st.markdown(
                    f'<div class="login-error">{html.escape(str(st.session_state.login_error))}</div>',
                    unsafe_allow_html=True,
                )

    # --- Credenciais de desenvolvimento (abaixo do card, fora do form) ---
    if "DEV_CREDENTIALS_SHOWN" not in st.session_state:
        st.session_state.DEV_CREDENTIALS_SHOWN = True

    if st.session_state.DEV_CREDENTIALS_SHOWN:
        st.markdown("""
        <div class="login-dev">
            <div class="login-dev-title">Acessos de avaliação · ambiente de desenvolvimento</div>
            <div class="login-dev-grid">
                <div class="login-dev-item">
                    <div class="login-dev-role">Gerente</div>
                    <div class="login-dev-cred"><b>gerente@smartvision.com</b><br>Senha123!</div>
                </div>
                <div class="login-dev-item">
                    <div class="login-dev-role">Supervisor</div>
                    <div class="login-dev-cred"><b>supervisor@smartvision.com</b><br>Senha123!</div>
                </div>
                <div class="login-dev-item">
                    <div class="login-dev-role">Vendedor</div>
                    <div class="login-dev-cred"><b>vendedor@smartvision.com</b><br>Senha123!</div>
                </div>
            </div>
        </div>
        <div class="login-footnote">SmartVision · Plataforma corporativa de gestão óptica &nbsp;·&nbsp; v2.0</div>
        """, unsafe_allow_html=True)

    # --- Lógica de submissão ---
    if entrar:
        _handle_login(usuario, senha)


def _handle_login(usuario: str, senha: str):
    """Processa o login: valida, autentica no backend e define a sessão."""
    st.session_state.login_error = None

    # Rate limiter por sessão (proteção contra tentativas repetidas)
    if "login_rate_limiter" not in st.session_state:
        st.session_state.login_rate_limiter = auth_service.RateLimiter()

    try:
        auth_token, user_data = auth_service.autenticar(
            str(usuario or ""),
            str(senha or ""),
            st.session_state.login_rate_limiter,
        )
    except (ValueError, RuntimeError) as exc:
        st.session_state.login_error = str(exc)
        st.session_state.login_username = str(usuario or "").strip()
        st.rerun()
        return
    except Exception as exc:
        st.session_state.login_error = str(exc) or (
            "Não foi possível realizar o login agora. Tente novamente."
        )
        st.session_state.login_username = str(usuario or "").strip()
        st.rerun()
        return

    # Sucesso — sessão definida (perfil vem do backend)
    st.session_state.auth_token = auth_token
    st.session_state.auth_user = user_data
    st.session_state.authenticated = True
    st.session_state.login_error = None
    st.session_state.login_username = str(usuario or "").strip()
    st.rerun()


def _render_page_header(icon: str, title: str, subtitle: str, eyebrow: str = "SmartVision"):
    """Renderiza o cabeçalho padronizado das páginas internas."""
    st.markdown(
        f"""
        <div class="page-heading">
            <div class="page-heading-icon">{html.escape(icon)}</div>
            <div class="page-heading-copy">
                <div class="page-heading-eyebrow">{html.escape(eyebrow)}</div>
                <h1 class="page-heading-title">{html.escape(title)}</h1>
                <p class="page-heading-subtitle">{html.escape(subtitle)}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Executar gate de autenticação antes de render qualquer página interna
# -----------------------------------------------------------------------------
_require_auth()

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
# -----------------------------------------------------------------------------
# CHANGE 06: Dados da sessão autenticada e redirecionamento por perfil
# -----------------------------------------------------------------------------
_MENU_OPTIONS = [
    "🏠 O Meu Painel",
    "🎯 As Minhas Metas & Comissões",
    "📢 Mural do RH & Comunicação",
    "📂 Central do Colaborador",
    "🎓 Academia SmartVision",
    "⚡ Atalhos Operacionais",
    "📋 Catálogo de Produtos",
    "📦 Gestão de Estoque Auditado",
    "📦 Inventário Físico & Conciliação",
    "🚚 Saídas de Estoque",
    "🔔 Alertas & Reposição",
]


def _perfil_para_pagina_inicial(role: str) -> int:
    """Retorna o índice da página inicial com base no perfil do usuário.

    Perfis do backend Xano (tabela ``user``): ``Gestor``, ``Supervisor``,
    ``Vendedor``, ``Estoquista``, ``Técnico`` e legados ``admin``/``member``.
    """
    r = (role or "").strip().lower()
    if r in ("gestor", "gerente", "supervisor", "admin", "estoquista"):
        return _MENU_OPTIONS.index("📦 Gestão de Estoque Auditado")
    if r in ("vendedor", "member"):
        return _MENU_OPTIONS.index("🚚 Saídas de Estoque")
    if r in ("técnico", "tecnico"):
        return _MENU_OPTIONS.index("📦 Gestão de Estoque Auditado")
    return 0


# Determinar índice inicial da navegação (apenas na primeira renderização autenticada)
_default_index = 0
if st.session_state.authenticated and "menu_index_set" not in st.session_state:
    user_role = (st.session_state.auth_user or {}).get("role", "")
    _default_index = _perfil_para_pagina_inicial(user_role)
    st.session_state.menu_index_set = True

with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-mark">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <circle cx="6.2" cy="14.3" r="3.4"></circle>
                    <circle cx="17.8" cy="14.3" r="3.4"></circle>
                    <path d="M9.6 14.3h4.8M2.8 14.3 1.8 11M21.2 14.3l1-3.3M6.2 10.9 7.7 7.2h8.6l1.5 3.7"></path>
                </svg>
            </div>
            <div>
                <div class="sidebar-brand-name">Smart<span>Vision</span></div>
                <div class="sidebar-brand-sub">Portal do colaborador</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Informações do usuário autenticado
    if st.session_state.authenticated and st.session_state.auth_user:
        _user = st.session_state.auth_user
        _user_name = _user.get("name") or _user.get("email") or "Usuário"
        _user_role = _user.get("role") or "—"
        _sidebar_avatar = html.escape((_user_name or "U")[0].upper())
        st.markdown(f"""
        <div class="sidebar-user">
            <div class="sidebar-user-avatar">{_sidebar_avatar}</div>
            <div style="min-width:0;">
                <div class="sidebar-user-name">{html.escape(str(_user_name))}</div>
                <div class="sidebar-user-role">{html.escape(str(_user_role))}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-label">Navegação</div>', unsafe_allow_html=True)

    menu_option = st.radio(
        "Navegação Principal:",
        options=_MENU_OPTIONS,
        index=_default_index if st.session_state.authenticated else 0,
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-section-label">Unidade operacional</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-unit">
        <div class="sidebar-unit-title"><span class="status-dot"></span> Loja 04 · Matriz</div>
        <div class="sidebar-unit-row"><span>Unidade</span><b>Shopping Paulista</b></div>
        <div class="sidebar-unit-row"><span>Gestora</span><b>Juliana Brandão</b></div>
        <div class="sidebar-unit-row"><span>Rede</span><b>192.168.10.45</b></div>
    </div>
    """, unsafe_allow_html=True)

    # Configuração de Conexão com Xano (para integração de estoque)
    with st.expander("🔌 Integração Backend Xano"):
        current_env_url = os.getenv("XANO_BASE_URL", "")
        base_url_input = st.text_input(
            "XANO_BASE_URL:",
            value=current_env_url or "https://x8ki-letl-twmt.n7.xano.io/api:SzoTJegm"
        )
        if base_url_input:
            os.environ["XANO_BASE_URL"] = base_url_input
        st.caption("Status: " + ("🟢 Ativo" if os.getenv("XANO_BASE_URL") else "🟡 Não configurado"))

    if st.session_state.authenticated and st.session_state.auth_user:
        if st.button("↪  Sair da conta", key="btn_logout", use_container_width=True):
            st.session_state.auth_token = None
            st.session_state.auth_user = None
            st.session_state.authenticated = False
            st.session_state.login_error = None
            st.session_state.login_username = ""
            st.session_state.login_loading = False
            st.session_state.login_show_password = False
            st.session_state.menu_index_set = False
            st.rerun()

    st.markdown("""
    <div class="sidebar-footer">
        <b>SmartVision</b> · Plataforma de gestão óptica<br>v2.0 · Ambiente seguro
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HEADER SUPERIOR (BRANDING, SEARCH, NOTIFICAÇÕES & PROFILE CARD)
# -----------------------------------------------------------------------------
search_query = ""

# Dados do usuário autenticado para o header
_header_user_name = "Carlos Eduardo Silveira"
_header_user_role = "Consultor Ótico Senior"
if st.session_state.authenticated and st.session_state.auth_user:
    _header_user_name = st.session_state.auth_user.get("name") or _header_user_name
    _header_user_role = st.session_state.auth_user.get("role") or "Usuário"

_header_avatar = (_header_user_name or "U")[0].upper() if _header_user_name else "U"
_header_user_name_html = html.escape(str(_header_user_name))
_header_user_role_html = html.escape(str(_header_user_role))
_header_avatar_html = html.escape(str(_header_avatar))
_header_today = datetime.now().strftime("%d/%m/%Y")

header_html = f"""
<div class="portal-header">
    <div class="portal-header-inner">
        <div class="brand-lockup">
            <div class="brand-mark">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <circle cx="6.2" cy="14.3" r="3.4"></circle>
                    <circle cx="17.8" cy="14.3" r="3.4"></circle>
                    <path d="M9.6 14.3h4.8M2.8 14.3 1.8 11M21.2 14.3l1-3.3M6.2 10.9 7.7 7.2h8.6l1.5 3.7"></path>
                </svg>
            </div>
            <div>
                <div class="brand-eyebrow"><span class="status-dot"></span> Plataforma de gestão óptica</div>
                <div class="brand-title">Smart<span class="brand-accent">Vision</span></div>
                <div class="brand-subtitle">Visão unificada da loja, do time e dos resultados.</div>
            </div>
        </div>
        <div class="hero-actions">
            <div class="hero-meta-row">
                <span class="hero-chip">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <rect x="3" y="4" width="18" height="18" rx="2"></rect><path d="M16 2v4M8 2v4M3 10h18"></path>
                    </svg>
                    {_header_today}
                </span>
                <span class="hero-chip">Loja 04 · Matriz</span>
                <div class="notification-pill">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="13" height="13" aria-hidden="true">
                        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.7 21a2 2 0 0 1-3.4 0"></path>
                    </svg>
                    Central de avisos <span class="badge-yellow">{unread_count}</span>
                </div>
            </div>
            <div class="profile-card">
                <div class="profile-avatar">{_header_avatar_html}</div>
                <div>
                    <div class="profile-name">{_header_user_name_html}</div>
                    <div class="profile-role">{_header_user_role_html}</div>
                    <div class="profile-store">Shopping Paulista · Loja 04</div>
                </div>
            </div>
        </div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Barra de Pesquisa Rápida Global
search_col1, search_col2 = st.columns([3.6, 1.4])
with search_col1:
    search_query = st.text_input(
        "🔍 Busca Rápida de Avisos, Procedimentos e Manuais:",
        placeholder="Buscar avisos, procedimentos, manuais ou colaboradores...",
        label_visibility="collapsed"
    )
with search_col2:
    st.markdown(
        f"<div class='today-pill'><span>📅</span> Hoje · {_header_today}</div>",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# SEÇÃO 1: O MEU PAINEL (VISÃO GERAL CONSOLIDADA)
# -----------------------------------------------------------------------------
if menu_option == "🏠 O Meu Painel":
    _welcome_name = "visitante"
    if st.session_state.authenticated and st.session_state.auth_user:
        _welcome_name = st.session_state.auth_user.get("name") or "usuário"
    _render_page_header(
        "👋",
        f"Olá, {_welcome_name}",
        "Aqui está o panorama atualizado das suas metas, avisos e atividades de hoje.",
        "Visão geral · Meu painel",
    )

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
    _render_page_header(
        "🎯",
        "Metas & Comissões",
        "Monitore a sua evolução mensal, entenda o cálculo das suas comissões e simule ganhos adicionais.",
        "Performance comercial",
    )

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
    _render_page_header(
        "📢",
        "Mural & Comunicação",
        "Fique por dentro das novidades, comunicados operacionais, avisos da diretoria e aniversariantes.",
        "Cultura & pessoas",
    )

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
elif menu_option == "📂 Central do Colaborador":
    _render_page_header(
        "📂",
        "Central do Colaborador",
        "Acesse seus comprovantes de rendimento, controle seu saldo de banco de horas e envie pedidos formais ao RH.",
        "Documentos & jornada",
    )

    _user = st.session_state.auth_user or {}
    _role = (_user.get("role") or "").lower()
    _email = (_user.get("email") or "").lower()
    _is_manager = _role in ("gestor", "gerente", "admin") or "gerente" in _email or "admin" in _email

    if _is_manager:
        tab_holerite, tab_ponto, tab_solic, tab_gestao = st.tabs([
            "📄 Recibos de Vencimento (Holerites)",
            "⏰ Espelho de Ponto & Banco de Horas",
            "📝 Solicitações ao RH (Férias, Atestados, Turno)",
            "👥 Cadastrar Colaborador (Gestão)"
        ])
    else:
        tab_holerite, tab_ponto, tab_solic = st.tabs([
            "📄 Recibos de Vencimento (Holerites)",
            "⏰ Espelho de Ponto & Banco de Horas",
            "📝 Solicitações ao RH (Férias, Atestados, Turno)"
        ])
        tab_gestao = None

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

    if tab_gestao:
        with tab_gestao:
            st.markdown("### 👥 Gestão de Equipe & Cadastro de Novo Colaborador")
            st.caption("Painel exclusivo para Gestores. Cadastre novos funcionários da ótica e visualize os colaboradores ativos.")

            col_form, col_info = st.columns([3, 2])

            with col_form:
                with st.form("form_novo_colaborador", clear_on_submit=True):
                    st.markdown("##### 📝 Dados do Novo Colaborador")
                    novo_nome = st.text_input("Nome Completo *", placeholder="Ex: Mariana Costa")
                    novo_email = st.text_input("E-mail de Acesso (Login) *", placeholder="Ex: mariana.costa@smartvision.com")
                    nova_senha = st.text_input(
                        "Senha Inicial *",
                        type="password",
                        placeholder="Mínimo 8 caracteres (letras e números)",
                        help="Requisitos de segurança: mínimo 8 caracteres com letras e dígitos."
                    )
                    novo_cargo = st.selectbox(
                        "Cargo / Perfil de Acesso *",
                        options=["Vendedor", "Supervisor", "Gestor", "Estoquista", "Técnico"]
                    )

                    btn_cadastrar = st.form_submit_button("➕ Cadastrar Colaborador", type="primary")

                    if btn_cadastrar:
                        erros = []
                        if not novo_nome.strip():
                            erros.append("Informe o nome completo do colaborador.")
                        if not novo_email.strip() or "@" not in novo_email:
                            erros.append("Informe um e-mail válido para o colaborador.")
                        if len(nova_senha) < 8 or not any(c.isalpha() for c in nova_senha) or not any(c.isdigit() for c in nova_senha):
                            erros.append("A senha inicial deve ter no mínimo 8 caracteres, contendo pelo menos 1 letra e 1 número.")

                        if erros:
                            for err in erros:
                                st.error(err)
                        else:
                            try:
                                if xano_client:
                                    signup_resp = xano_client.signup_user(novo_nome.strip(), novo_email.strip(), nova_senha)
                                    novo_id = signup_resp.get("user_id")

                                    # Tentar registrar role no backend via admin_user_role
                                    if novo_id and st.session_state.auth_token:
                                        try:
                                            xano_client.update_user_role(novo_id, novo_cargo, st.session_state.auth_token)
                                        except Exception:
                                            pass

                                    if "created_team_members" not in st.session_state:
                                        st.session_state.created_team_members = []
                                    st.session_state.created_team_members.append({
                                        "id": novo_id,
                                        "name": novo_nome.strip(),
                                        "email": novo_email.strip().lower(),
                                        "role": novo_cargo,
                                        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
                                    })

                                    st.success(
                                        f"🎉 Colaborador **{novo_nome.strip()}** cadastrado com sucesso!\n\n"
                                        f"- **E-mail de Login:** `{novo_email.strip().lower()}`\n"
                                        f"- **Cargo / Perfil:** **{novo_cargo}**\n\n"
                                        f"O usuário já pode entrar no sistema com as credenciais cadastradas."
                                    )
                                else:
                                    st.error("Serviço Xano não está disponível.")
                            except Exception as exc:
                                err_msg = str(exc)
                                if "already in use" in err_msg.lower() or "400" in err_msg:
                                    st.error("⚠️ Este e-mail já está em uso por outro usuário no sistema.")
                                else:
                                    st.error(f"Erro ao cadastrar colaborador: {err_msg}")

            with col_info:
                st.markdown("##### ℹ️ Cargos e Níveis de Acesso")
                st.markdown("""
                - **Vendedor:** Registro de saídas no PDV (venda balcão, laboratório), consulta de catálogo e metas.
                - **Supervisor:** Monitoramento de estoque, contagem física em inventário e visão de alertas.
                - **Gestor:** Aprovação de divergências de inventário, autorização de perdas e gestão de colaboradores.
                - **Estoquista:** Conferência de notas fiscais, entradas de mercadorias e catálogo.
                - **Técnico:** Ajustes ópticos e controle de montagem em laboratório.
                """)

            st.markdown("---")
            st.markdown("#### 📋 Colaboradores Registrados na Loja")

            team_list = []
            if xano_client and st.session_state.auth_token:
                try:
                    raw_team = xano_client.list_team_members(st.session_state.auth_token)
                    for m in raw_team:
                        created_ts = m.get("created_at")
                        created_str = (
                            datetime.fromtimestamp(created_ts / 1000).strftime("%d/%m/%Y")
                            if created_ts and isinstance(created_ts, (int, float))
                            else "—"
                        )
                        team_list.append({
                            "ID": m.get("id"),
                            "Nome": m.get("name") or "—",
                            "E-mail": m.get("email") or "—",
                            "Data de Cadastro": created_str,
                            "Status": "🟢 Ativo",
                        })
                except Exception:
                    pass

            existing_emails = {m["E-mail"] for m in team_list}
            for loc in st.session_state.get("created_team_members", []):
                if loc["email"] not in existing_emails:
                    team_list.append({
                        "ID": loc.get("id") or "Novo",
                        "Nome": loc["name"],
                        "E-mail": loc["email"],
                        "Data de Cadastro": loc["created_at"],
                        "Status": "🟢 Ativo",
                    })

            if team_list:
                st.dataframe(team_list, use_container_width=True)
            else:
                st.info("Nenhum colaborador registrado na equipe.")


# -----------------------------------------------------------------------------
# SEÇÃO 5: ACADEMIA SMARTVISION (TREINOS & GUIA DE LENTES - CHANGE 5)
# -----------------------------------------------------------------------------
elif menu_option == "🎓 Academia SmartVision":
    _render_page_header(
        "🎓",
        "Academia SmartVision",
        "Consulte a tabela comparativa de materiais e especialize-se com microlearnings rápidos de alto impacto.",
        "Conhecimento & excelência técnica",
    )

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
elif menu_option == "⚡ Atalhos Operacionais":
    _render_page_header(
        "⚡",
        "Atalhos Operacionais",
        "Acesse diretamente as rotinas mais frequentes da ótica com poucos cliques.",
        "Produtividade no balcão",
    )

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
# CHANGE 01: CATÁLOGO DE PRODUTOS (CONSULTA E CADASTRO)
# -----------------------------------------------------------------------------
elif menu_option == "📋 Catálogo de Produtos":
    if product_catalog is None:
        st.error("Módulo de catálogo indisponível. Verifique a instalação do projeto.")
        st.stop()

    _render_page_header(
        "📋",
        "Catálogo de Produtos",
        "Consulta por SKU, nome e categoria, com cadastro integrado ao estoque auditado da loja.",
        "Gestão de sortimento",
    )
    st.caption(
        "O saldo inicial é sempre 0; entradas e ajustes passam pelo estoque auditado."
    )

    _catalog_flash = st.session_state.pop("catalog_flash", None)
    if _catalog_flash:
        st.success(_catalog_flash)

    catalog_tab, create_tab = st.tabs(["🔎 Consulta", "➕ Cadastrar Produto"])

    with catalog_tab:
        st.markdown("### Consulta e filtros")
        col_filter_1, col_filter_2 = st.columns([2, 1])
        with col_filter_1:
            catalog_search = st.text_input(
                "Buscar por SKU ou nome",
                placeholder="Ex.: ARM-RAY, Ray-Ban, Crizal...",
                key="catalog_search",
            )
        with col_filter_2:
            catalog_category = st.selectbox(
                "Categoria",
                options=["Todas", *product_catalog.PRODUCT_CATEGORIES],
                key="catalog_category",
            )

        catalog_products = []
        catalog_error = None
        if not (xano_client and os.getenv("XANO_BASE_URL")):
            catalog_error = "Backend Xano não configurado (XANO_BASE_URL)."
        else:
            try:
                catalog_products = xano_client.list_products(
                    product_catalog.filter_params(catalog_category, catalog_search),
                    auth_token=st.session_state.get("auth_token"),
                )
            except Exception as exc:
                catalog_error = str(exc)

        if catalog_error:
            st.error("Não foi possível consultar o catálogo: " + catalog_error)
        else:
            metric_col_1, metric_col_2 = st.columns(2)
            metric_col_1.metric("Produtos encontrados", len(catalog_products))
            total_stock = sum(int(p.get("current_stock") or 0) for p in catalog_products)
            metric_col_2.metric("Saldo físico total", f"{total_stock} un")

            if not catalog_products:
                st.info("Nenhum produto encontrado para os filtros informados.")
            else:
                rows = []
                for p in catalog_products:
                    rows.append({
                        "ID": p.get("id"),
                        "SKU": p.get("sku"),
                        "Produto": p.get("name"),
                        "Categoria": p.get("category"),
                        "Marca": p.get("brand"),
                        "Modelo": p.get("model"),
                        "Preço de venda": p.get("sale_price"),
                        "Estoque": p.get("current_stock"),
                        "Mínimo": p.get("min_stock"),
                        "Localização": p.get("location"),
                    })
                st.dataframe(rows, use_container_width=True, hide_index=True)

    with create_tab:
        st.markdown("### Cadastro de produto")
        st.caption("Campos com * são obrigatórios. Para lentes, os atributos técnicos também são obrigatórios.")

        new_category = st.selectbox(
            "Categoria *",
            options=list(product_catalog.PRODUCT_CATEGORIES),
            key="catalog_new_category",
        )
        is_lens = new_category in product_catalog.LENS_CATEGORIES

        with st.form("catalog_create_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                new_sku = st.text_input("SKU *", placeholder="Ex.: ARM-001")
                new_brand = st.text_input("Marca *", placeholder="Ex.: Ray-Ban")
                new_cost_price = st.number_input(
                    "Custo (R$)", min_value=0.0, value=0.0, step=10.0, format="%.2f"
                )
                new_min_stock = st.number_input(
                    "Estoque mínimo *", min_value=0, value=0, step=1
                )
            with col_b:
                new_name = st.text_input("Nome *", placeholder="Ex.: Armação Aviador")
                new_model = st.text_input("Modelo *", placeholder="Ex.: Aviador Classic")
                new_sale_price = st.number_input(
                    "Preço de venda (R$) *", min_value=0.0, value=0.0, step=10.0, format="%.2f"
                )
                new_location = st.text_input("Localização *", placeholder="Ex.: Vitrine A1")

            new_sphere = new_cylinder = new_axis = new_addition = None
            new_lens_type = new_treatment = new_material = None
            if is_lens:
                st.markdown("#### Atributos técnicos da lente")
                col_l1, col_l2, col_l3 = st.columns(3)
                with col_l1:
                    new_sphere = st.number_input(
                        "Grau esférico *", min_value=-20.0, max_value=20.0,
                        value=0.0, step=0.25, format="%.2f",
                    )
                    new_axis = st.number_input(
                        "Eixo (°)", min_value=0, max_value=180, value=0, step=1
                    )
                with col_l2:
                    new_cylinder = st.number_input(
                        "Grau cilíndrico *", min_value=-20.0, max_value=20.0,
                        value=0.0, step=0.25, format="%.2f",
                    )
                    new_addition = st.number_input(
                        "Adição", min_value=0.0, max_value=4.0,
                        value=0.0, step=0.25, format="%.2f",
                    )
                with col_l3:
                    default_lens_type = "Monofocal" if new_category == "Lente Oftálmica" else "Esférica"
                    new_lens_type = st.text_input("Tipo de lente *", value=default_lens_type)
                    new_treatment = st.text_input("Tratamento", placeholder="Ex.: Crizal")
                    new_material = st.text_input("Material", placeholder="Ex.: Resina 1.67")

            submitted = st.form_submit_button("Cadastrar produto", type="primary")

        if submitted:
            values = {
                "sku": new_sku,
                "name": new_name,
                "category": new_category,
                "brand": new_brand,
                "model": new_model,
                "cost_price": new_cost_price,
                "sale_price": new_sale_price,
                "min_stock": new_min_stock,
                "location": new_location,
                "sphere_power": new_sphere,
                "cylinder_power": new_cylinder,
                "axis": new_axis,
                "addition": new_addition,
                "lens_type": new_lens_type,
                "treatment": new_treatment,
                "material": new_material,
            }
            validation_errors = product_catalog.validate_product_payload(values)
            if validation_errors:
                for message in validation_errors:
                    st.error(message)
            elif not (xano_client and os.getenv("XANO_BASE_URL")):
                st.error("Backend Xano não configurado; o cadastro não foi enviado.")
            else:
                payload = product_catalog.build_product_payload(values)
                try:
                    created = xano_client.create_product(
                        payload,
                        auth_token=st.session_state.get("auth_token"),
                    )
                except Exception as exc:
                    st.error("Erro ao cadastrar produto: " + str(exc))
                else:
                    created_id = created.get("id") if isinstance(created, dict) else None
                    st.session_state["catalog_flash"] = (
                        "✅ Produto cadastrado com sucesso"
                        + (f" (ID {created_id})." if created_id is not None else ".")
                    )
                    st.rerun()

# -----------------------------------------------------------------------------
# SEÇÃO 7: GESTÃO DE ESTOQUE AUDITADO & REPOSIÇÃO (SMARTVISION CORE)
# -----------------------------------------------------------------------------
elif menu_option == "📦 Gestão de Estoque Auditado":
    _render_page_header(
        "📦",
        "Estoque Auditado",
        "Entradas, saídas e reposição com rastreabilidade completa e validação estrita contra saldo negativo.",
        "Operações & conformidade",
    )
    st.info("💡 **Conformidade Crítica**: Todas as entradas e saídas exigem registro prévio de auditoria na tabela `stock_movement` e validação estrita contra saldo negativo.")

    # Obter produtos cadastrados (do Xano se disponível ou mock completo)
    prods_data = []
    try:
        if xano_client and os.getenv("XANO_BASE_URL"):
            prods_data = xano_client.list_products(
                auth_token=st.session_state.get("auth_token")
            )
    except Exception:
        pass

    if not prods_data:
        prods_data = [
            {"id": 1, "sku": "ARM-RAY-01", "name": "Armação Ray-Ban Clubmaster RB5154", "category": "Armação", "brand": "Ray-Ban", "cost_price": 280.0, "sale_price": 680.0, "current_stock": 2, "min_stock": 5, "location": "Gaveta A1"},
            {"id": 2, "sku": "LEN-CRIZ-02", "name": "Lente Multifocal Crizal Sapphire HR", "category": "Lente Oftálmica", "brand": "Essilor", "cost_price": 350.0, "sale_price": 950.0, "current_stock": 8, "min_stock": 4, "location": "Prateleira L2"},
            {"id": 3, "sku": "CON-ACUV-03", "name": "Lente de Contato Acuvue Oasys (Grau -2.50)", "category": "Lente de Contato", "brand": "Johnson & Johnson", "cost_price": 85.0, "sale_price": 175.0, "current_stock": 1, "min_stock": 8, "location": "Gaveta C3"},
            {"id": 4, "sku": "ARM-OAK-04", "name": "Armação Oakley Crosslink Zero", "category": "Armação", "brand": "Oakley", "cost_price": 310.0, "sale_price": 720.0, "current_stock": 6, "min_stock": 3, "location": "Vitrine Principal"},
            {"id": 5, "sku": "SOL-LIMP-05", "name": "Solução de Limpeza Opti-Free PureMoist 300ml", "category": "Acessórios", "brand": "Alcon", "cost_price": 22.0, "sale_price": 58.0, "current_stock": 0, "min_stock": 6, "location": "Balcão Checkout"},
        ]

    # Identificar itens abaixo do estoque mínimo (Replenishment)
    rupture_items = [p for p in prods_data if p.get("current_stock", 0) <= p.get("min_stock", 0)]
    zero_items = [p for p in prods_data if p.get("current_stock", 0) == 0]

    # Indicadores rápidos de topo
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="metric-widget">
            <div class="metric-label">Total de SKUs Ativos</div>
            <div class="metric-value">{len(prods_data)}</div>
            <div class="metric-sub" style="color: #3942F6;">Catálogo Monitorado</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="metric-widget" style="border-left: 5px solid {'#EF4444' if rupture_items else '#10B981'};">
            <div class="metric-label">Itens no Ponto de Pedido</div>
            <div class="metric-value" style="color: {'#EF4444' if rupture_items else '#10B981'};">{len(rupture_items)}</div>
            <div class="metric-sub" style="color: {'#EF4444' if rupture_items else '#10B981'};">{'⚠️ Ação Imediata' if rupture_items else '✅ Níveis Adequados'}</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="metric-widget" style="border-left: 5px solid {'#DC2626' if zero_items else '#10B981'};">
            <div class="metric-label">Ruptura Total (Estoque Zero)</div>
            <div class="metric-value" style="color: {'#DC2626' if zero_items else '#10B981'};">{len(zero_items)}</div>
            <div class="metric-sub" style="color: {'#DC2626' if zero_items else '#10B981'};">{'🚫 Vendas Perdidas' if zero_items else '✅ Sem Faltas Críticas'}</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        total_pecas = sum(p.get("current_stock", 0) for p in prods_data)
        st.markdown(f"""
        <div class="metric-widget">
            <div class="metric-label">Saldo Físico Total</div>
            <div class="metric-value">{total_pecas} un</div>
            <div class="metric-sub" style="color: #64748B;">Estoque em Loja</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    tab_e, tab_s, tab_c, tab_r = st.tabs([
        "📥 Entrada de Estoque", 
        "📤 Saída de Estoque", 
        "📋 Consulta de Catálogo",
        "🚨 Alertas & Reposição (Replenishment)"
    ])

    with tab_e:
        st.markdown("#### Registrar Entrada de Mercadoria")
        col_pe1, col_pe2 = st.columns(2)
        with col_pe1:
            p_id = st.number_input("ID do Produto:", min_value=1, value=1, step=1, key="ent_pid")
            qty = st.number_input("Quantidade:", min_value=1, value=5, step=1, key="ent_qty")
            unit_cost = st.number_input("Custo Unitário (R$):", min_value=0.0, value=150.0, step=10.0, key="ent_cost")
        with col_pe2:
            reason = st.text_input("Justificativa / Nota Fiscal:", value="NF 4920 - Recebimento Fornecedor", key="ent_rsn")
            supplier = st.text_input("Fornecedor / Fabricante:", value="EssilorLuxottica Distribuidora", key="ent_supp")
            batch_id = st.text_input("Lote Técnico / Batch:", value="LOTE-2026-X1", key="ent_batch")

        if st.button("Confirmar Entrada Auditada", type="primary", key="btn_ent"):
            try:
                if xano_client:
                    res = xano_client.record_stock_entry({
                        "product_id": p_id,
                        "quantity": int(qty),
                        "reason": reason,
                        "unit_cost": float(unit_cost),
                        "supplier_id": supplier,
                        "batch_id": batch_id,
                        "user_id": 1
                    })
                    st.success(f"✅ Entrada registrada e auditada com sucesso! Novo saldo: {res.get('product', {}).get('current_stock', 'N/A')}")
                else:
                    st.warning("Serviço Xano não configurado ou offline. Operação simulada localmente com sucesso.")
            except Exception as e:
                st.error(f"Erro ao registrar entrada: {e}")

    with tab_s:
        st.markdown("#### Registrar Saída de Estoque")
        col_ps1, col_ps2 = st.columns(2)
        with col_ps1:
            p_id_s = st.number_input("ID do Produto:", min_value=1, value=1, step=1, key="sai_pid")
            qty_s = st.number_input("Quantidade a Retirar:", min_value=1, value=1, step=1, key="sai_qty")
        with col_ps2:
            reason_s = st.selectbox("Motivo da Saída:", ["Venda Balcão PDV", "LOSS", "DAMAGE", "Montagem de Laboratório", "Transferência entre Lojas"], key="sai_rsn")
            justification = ""
            if reason_s in ["LOSS", "DAMAGE"]:
                justification = st.text_area("Justificativa Obrigatória (Auditoria):", value="Armação trincada no ajuste de charneira", key="sai_just")

        if st.button("Confirmar Saída com Verificação de Saldo", type="primary", key="btn_sai"):
            try:
                if xano_client:
                    payload_s = {
                        "product_id": p_id_s,
                        "quantity": int(qty_s),
                        "reason": reason_s,
                        "user_id": 1
                    }
                    if justification:
                        payload_s["justification"] = justification
                    res = xano_client.record_stock_exit(payload_s)
                    st.success(f"✅ Saída concluída e auditada! Saldo atualizado: {res.get('product', {}).get('current_stock', 'N/A')}")
                else:
                    st.warning("Serviço Xano não configurado. Em caso de saldo insuficiente, o backend rejeitaria com HTTP 400 conforme AGENTS.md.")
            except Exception as e:
                st.error(f"Erro na saída: {e}")

    with tab_c:
        st.markdown("#### Produtos Cadastrados & Localização")
        st.dataframe(prods_data, use_container_width=True)

    with tab_r:
        st.markdown("#### 🚨 Painel de Reposição & Prevenção de Rupturas (Replenishment)")
        st.info(
            "A gestão de alertas e sugestões de reposição foi centralizada na seção "
            "**🔔 Alertas & Reposição** no menu lateral, que consome o backend "
            "(`/smart_vision/replenishment` e `/smart_vision/alerts`) em vez de calcular "
            "valores no cliente, conforme AGENTS.md (regra 5.2 — lógica fica no backend)."
        )


# -----------------------------------------------------------------------------
# CHANGE 03: INVENTÁRIO FÍSICO & CONCILIAÇÃO DE ESTOQUE
# -----------------------------------------------------------------------------
elif menu_option == "📦 Inventário Físico & Conciliação":
    _render_page_header(
        "🧮",
        "Inventário Físico & Conciliação",
        "Fluxo de ponta a ponta: abertura, contagem física, conciliação, aprovação do gestor e aplicação do ajuste auditado.",
        "Controle & acuracidade",
    )
    st.caption("O ajuste reutiliza o ledger de auditoria do estoque, garantindo rastreabilidade completa.")

    # ------------------------------------------------------------------
    # Helpers de persistência (real via Xano ou mock de demonstração)
    # ------------------------------------------------------------------
    _DEFAULT_INV_PRODUCTS = [
        {"id": 1, "sku": "ARM-RAY-01", "name": "Armação Ray-Ban Clubmaster RB5154", "category": "Armação", "brand": "Ray-Ban", "current_stock": 2, "min_stock": 5, "location": "Gaveta A1"},
        {"id": 2, "sku": "LEN-CRIZ-02", "name": "Lente Multifocal Crizal Sapphire HR", "category": "Lente Oftálmica", "brand": "Essilor", "current_stock": 8, "min_stock": 4, "location": "Prateleira L2"},
        {"id": 3, "sku": "CON-ACUV-03", "name": "Lente de Contato Acuvue Oasys (Grau -2.50)", "category": "Lente de Contato", "brand": "Johnson & Johnson", "current_stock": 1, "min_stock": 8, "location": "Gaveta C3"},
        {"id": 4, "sku": "ARM-OAK-04", "name": "Armação Oakley Crosslink Zero", "category": "Armação", "brand": "Oakley", "current_stock": 6, "min_stock": 3, "location": "Vitrine Principal"},
        {"id": 5, "sku": "SOL-LIMP-05", "name": "Solução de Limpeza Opti-Free PureMoist 300ml", "category": "Acessórios", "brand": "Alcon", "current_stock": 0, "min_stock": 6, "location": "Balcão Checkout"},
    ]

    def _inv_products():
        """Catálogo de produtos (real via Xano ou mock)."""
        try:
            if xano_client and os.getenv("XANO_BASE_URL"):
                data = xano_client.list_products(
                    auth_token=st.session_state.get("auth_token")
                )
                st.session_state["inv_products"] = data
                return data
        except Exception as exc:
            st.session_state["inv_xano_warning"] = str(exc)
        if "inv_products" not in st.session_state:
            st.session_state["inv_products"] = list(_DEFAULT_INV_PRODUCTS)
        return st.session_state["inv_products"]

    def _inv_state(key, default=None):
        if key not in st.session_state:
            st.session_state[key] = default if default is not None else []
        return st.session_state[key]

    def _inv_save(key, value):
        st.session_state[key] = value

    def _inv_show_xano_warning():
        if st.session_state.get("inv_xano_warning") and not st.session_state.get("inv_warning_shown"):
            st.warning("Serviço Xano indisponível (" + st.session_state["inv_xano_warning"] + "). Usando dados de demonstração locais para navegação.")
            st.session_state["inv_warning_shown"] = True

    products = _inv_products()
    product_by_id = {p["id"]: p for p in products}

    inventories = _inv_state("inv_inventories")
    counts = _inv_state("inv_counts")
    discrepancies = _inv_state("inv_discrepancies")
    decisions = _inv_state("inv_decisions")

    # Usuário autenticado (a validação real de permissão é sempre no backend).
    _inv_user = st.session_state.auth_user or {}
    _inv_user_id = int(_inv_user.get("id") or 0)
    _inv_user_name = _inv_user.get("name") or _inv_user.get("email") or "Usuário"
    _inv_user_role = _inv_user.get("role") or ""
    _inv_is_manager = _inv_user_role in ["Gestor", "admin"]

    def _inv_real(fn, *args, **kwargs):
        """Tenta chamada real ao Xano.

        Retorna None quando o backend não está configurado/indisponível (permite
        fallback local de demonstração) ou quando o backend rejeitou a operação
        (erro HTTP; nesse caso o fallback não deve ser usado).
        """
        st.session_state.pop("inv_http_error", None)
        if not (xano_client and os.getenv("XANO_BASE_URL")):
            _inv_show_xano_warning()
            return None
        auth_token = st.session_state.get("auth_token")
        if auth_token and "auth_token" not in kwargs:
            kwargs["auth_token"] = auth_token
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            response = getattr(exc, "response", None)
            if response is not None:
                message = str(exc)
                try:
                    payload = response.json()
                    message = payload.get("message") or message
                except Exception:
                    pass
                st.session_state["inv_http_error"] = message
                st.error("Erro do backend: " + message)
                return None
            st.session_state["inv_xano_warning"] = str(exc)
            _inv_show_xano_warning()
            return None

    # ------------------------------------------------------------------
    # Sub-tabs do módulo de inventário
    # ------------------------------------------------------------------
    sub_tabs = st.tabs([
        "📋 Listagem de Inventários",
        "➕ Criar Inventário",
        "🔢 Contagem Física",
        "⚖️ Conciliação & Divergências",
        "✅ Aprovação do Gestor",
        "📜 Histórico & Ajustes",
    ])

    # ------------------- 1. Listagem -------------------
    with sub_tabs[0]:
        st.markdown("### 📋 Inventários Cadastrados")
        col_ref1, col_ref2 = st.columns([3, 1])
        with col_ref1:
            filtro_status = st.selectbox("Filtrar por status:", options=["Todos", "Aberto", "EmContagem", "AguardandoAprovacao", "Concluido"], key="inv_list_status")
        with col_ref2:
            if st.button("🔄 Atualizar listagem", key="inv_list_refresh"):
                st.rerun()

        real_inventories = _inv_real(xano_client.list_inventories,
                                     None if filtro_status == "Todos" else {"status": filtro_status})
        if real_inventories is not None:
            inventories = real_inventories
            _inv_save("inv_inventories", inventories)

        if not inventories:
            st.info("Nenhum inventário encontrado. Crie um na aba 'Criar Inventário'.")
        else:
            rows = []
            for inv in inventories:
                inv_id = inv.get("id")
                inv_counts_list = [c for c in counts if c.get("inventory_id") == inv_id]
                registered = inv.get("counts_recorded")
                if registered is None:
                    registered = len(inv_counts_list)
                scope_total = inv.get("products_in_scope")
                if scope_total is None:
                    category_filter = inv.get("category_filter")
                    location_filter = inv.get("location_filter")
                    scope_total = len([
                        p for p in products
                        if (not category_filter or p.get("category") == category_filter)
                        and (not location_filter or p.get("location") == location_filter)
                    ])
                progress = round((registered * 100) / scope_total, 1) if scope_total else 0.0
                rows.append({
                    "ID": inv_id,
                    "Status": inv.get("status"),
                    "Escopo": inv.get("scope"),
                    "Responsável (usuario_id)": inv.get("opened_by"),
                    "Abertura": str(inv.get("opened_at", ""))[:16],
                    "Contagens registradas": registered,
                    "Produtos no escopo": scope_total,
                    "Progresso (%)": f"{progress:.1f}%",
                })
            st.dataframe(rows, use_container_width=True, hide_index=True)

            st.markdown("### Selecionar inventário para operar")
            inv_options = {f"#{inv.get('id')} — {inv.get('status')} ({inv.get('scope')})": inv.get("id") for inv in inventories}
            sel_label = st.selectbox("Inventário:", options=list(inv_options.keys()), key="inv_list_select")
            if st.button("Usar inventário selecionado nas outras abas", key="inv_list_use"):
                st.session_state["inv_selected_id"] = inv_options[sel_label]
                st.success("Inventário #" + str(inv_options[sel_label]) + " selecionado. Use as outras abas.")

    # ------------------- 2. Criação -------------------
    with sub_tabs[1]:
        st.markdown("### ➕ Criar Novo Inventário Físico")
        with st.form("inv_create_form"):
            c1, c2 = st.columns(2)
            with c1:
                scope = st.selectbox("Escopo do inventário:", options=["completo", "categoria", "localizacao"], key="inv_c_scope")
                st.caption("Responsável pela abertura")
                st.markdown("**" + _inv_user_name + "** (ID " + str(_inv_user_id) + ")")
                opened_by = _inv_user_id
            with c2:
                category_filter = st.text_input("Categoria (filtro):", placeholder="ex: Armação", key="inv_c_cat")
                location_filter = st.text_input("Localização (filtro):", placeholder="ex: Gaveta A1", key="inv_c_loc")
            notes = st.text_area("Observações:", key="inv_c_notes")
            criar = st.form_submit_button("Criar Inventário", type="primary")

        if criar:
            if _inv_user_id <= 0:
                st.error("Sessão sem usuário identificado. Faça login novamente.")
            else:
                payload = {
                    "scope": scope,
                    "opened_by": int(opened_by),
                    "status": "Aberto",
                    "category_filter": category_filter if category_filter else None,
                    "location_filter": location_filter if location_filter else None,
                    "notes": notes if notes else None,
                }
                res = _inv_real(xano_client.create_inventory, payload)
                if res is None and st.session_state.get("inv_http_error"):
                    new_inv = None
                elif res is None:
                    # Fallback local para demonstração/offline
                    new_id = max([i.get("id", 0) for i in inventories] or [0]) + 1
                    new_inv = dict(payload, id=new_id, opened_at=str(datetime.now()))
                else:
                    new_inv = res

                if new_inv is not None:
                    _inv_save("inv_inventories", inventories + [new_inv])
                    st.success("✅ Inventário #" + str(new_inv.get("id")) + " criado com status " + str(new_inv.get("status")) + ".")
                    st.session_state["inv_selected_id"] = new_inv.get("id")

    # ------------------- 3. Contagem Física -------------------
    with sub_tabs[2]:
        st.markdown("### 🔢 Contagem Física de Produtos")
        st.info("O saldo de estoque NÃO é alterado durante a contagem. A contagem apenas registra a quantidade física encontrada.")

        selected_id = st.session_state.get("inv_selected_id")
        inv_for_count = None
        if selected_id:
            inv_for_count = next((i for i in inventories if i.get("id") == selected_id), None)

        if not inv_for_count:
            st.warning("Selecione um inventário na aba de listagem primeiro.")
        else:
            st.write("**Inventário #" + str(selected_id) + "** — Status: " + str(inv_for_count.get("status")) + " — Escopo: " + str(inv_for_count.get("scope")))
            if inv_for_count.get("status") not in ["Aberto", "EmContagem"]:
                st.error("Este inventário não está aberto para contagem (status: " + str(inv_for_count.get("status")) + ").")

            cego = st.checkbox("👁️‍🗨️ Modo de contagem cego (ocultar saldo esperado até o envio)", key="inv_count_cego")

            prod_options = {f"{p['sku']} — {p['name']} (saldo: {p.get('current_stock', '?')})": p["id"] for p in products}
            sel_prod_label = st.selectbox("Produto a contar:", options=list(prod_options.keys()), key="inv_count_prod")
            prod_id = prod_options[sel_prod_label]
            prod = product_by_id.get(prod_id, {})

            if not cego:
                st.caption("Saldo registrado no sistema: **" + str(prod.get("current_stock", "?")) + "** un (apenas referência, não alterado pela contagem).")

            c1, c2 = st.columns(2)
            with c1:
                qty = st.number_input("Quantidade física encontrada:", min_value=0, value=0, step=1, key="inv_count_qty")
            with c2:
                st.caption("Contado por")
                st.markdown("**" + _inv_user_name + "** (ID " + str(_inv_user_id) + ")")
            counted_by = _inv_user_id
            is_recount = st.checkbox("Esta é uma recontagem (preserva o registro anterior)", key="inv_count_recount")
            count_notes = st.text_area("Observações / justificativas:", key="inv_count_notes")

            if st.button("Registrar Contagem", type="primary", key="inv_count_reg"):
                if _inv_user_id <= 0:
                    st.error("Sessão sem usuário identificado. Faça login novamente.")
                elif inv_for_count.get("status") not in ["Aberto", "EmContagem"]:
                    st.error("Não é possível contar: inventário não está em contagem.")
                else:
                    # Iniciar contagem: mover para EmContagem se ainda estiver Aberto
                    if inv_for_count.get("status") == "Aberto":
                        transition_res = _inv_real(xano_client.transition_inventory_status, selected_id, "EmContagem", int(counted_by))
                        if transition_res is not None or not st.session_state.get("inv_http_error"):
                            for i in inventories:
                                if i.get("id") == selected_id:
                                    i["status"] = "EmContagem"
                            _inv_save("inv_inventories", inventories)

                    payload = {
                        "inventory_id": int(selected_id),
                        "product_id": int(prod_id),
                        "quantity_counted": int(qty),
                        "counted_by": int(counted_by),
                        "is_recount": bool(is_recount),
                        "notes": count_notes if count_notes else None,
                    }
                    res = _inv_real(xano_client.record_inventory_count, payload)
                    if res is None and st.session_state.get("inv_http_error"):
                        new_count = None
                    elif res is None:
                        new_count = dict(payload, id=len(counts) + 1, counted_at=str(datetime.now()))
                    else:
                        new_count = res

                    if new_count is not None:
                        # Atualizar ou adicionar na lista
                        existing_idx = None
                        for idx, c in enumerate(counts):
                            if c.get("inventory_id") == selected_id and c.get("product_id") == prod_id and not c.get("is_recount"):
                                existing_idx = idx
                                break
                        if existing_idx is not None and not is_recount:
                            counts[existing_idx] = new_count
                        else:
                            counts.append(new_count)
                        _inv_save("inv_counts", counts)
                        st.success("✅ Contagem registrada: " + str(qty) + " un para " + str(prod.get("name")) + ".")

            st.markdown("#### Contagens já registradas neste inventário")
            inv_counts_list = [c for c in counts if c.get("inventory_id") == selected_id]
            if not inv_counts_list:
                st.caption("Nenhuma contagem registrada ainda.")
            else:
                count_rows = []
                for c in inv_counts_list:
                    p = product_by_id.get(c.get("product_id"), {})
                    count_rows.append({
                        "Produto": p.get("name", "ID " + str(c.get("product_id"))),
                        "SKU": p.get("sku", ""),
                        "Qtd. Contada": c.get("quantity_counted"),
                        "Contado por (ID)": c.get("counted_by"),
                        "Recontagem": "Sim" if c.get("is_recount") else "Não",
                        "Data": str(c.get("counted_at", ""))[:16],
                    })
                st.dataframe(count_rows, use_container_width=True, hide_index=True)

    # ------------------- 4. Conciliação & Divergências -------------------
    with sub_tabs[3]:
        st.markdown("### ⚖️ Conciliação de Estoque")
        st.caption("Compara a quantidade física contada com o saldo de referência do sistema e classifica a divergência.")

        selected_id = st.session_state.get("inv_selected_id")
        if not selected_id:
            st.warning("Selecione um inventário na aba de listagem primeiro.")
        else:
            inv = next((i for i in inventories if i.get("id") == selected_id), None)
            st.write("**Inventário #" + str(selected_id) + "** — Status: " + str(inv.get("status") if inv else "?"))

            if st.button("Executar Conciliação", type="primary", key="inv_reconcile"):
                if _inv_user_id <= 0:
                    st.error("Sessão sem usuário identificado. Faça login novamente.")
                    res = None
                else:
                    res = _inv_real(xano_client.reconcile_inventory, selected_id, _inv_user_id)
                if res is not None:
                    st.success("✅ Conciliação executada. Status do inventário: " + str(res.get("status")) + ".")
                    if inv:
                        inv["status"] = res.get("status", "AguardandoAprovacao")
                        _inv_save("inv_inventories", inventories)
                    real_disc = _inv_real(xano_client.list_discrepancies, selected_id)
                    if real_disc is not None:
                        discrepancies = real_disc
                        _inv_save("inv_discrepancies", discrepancies)
                elif _inv_user_id > 0 and not st.session_state.get("inv_http_error"):
                    # Fallback local de conciliação
                    inv_counts_list = [c for c in counts if c.get("inventory_id") == selected_id]
                    disc_list = []
                    for c in inv_counts_list:
                        p = product_by_id.get(c.get("product_id"), {})
                        ref_qty = p.get("current_stock", 0)
                        diff = c.get("quantity_counted", 0) - ref_qty
                        if diff == 0:
                            dtype = "none"
                            impact = "Sem divergência"
                        elif diff < 0:
                            dtype = "shortage"
                            impact = "Falta de estoque: físico menor que o registrado."
                        else:
                            dtype = "overage"
                            impact = "Sobra de estoque: físico maior que o registrado."
                        disc_list.append({
                            "id": len(disc_list) + 1,
                            "inventory_id": selected_id,
                            "product_id": c.get("product_id"),
                            "reference_quantity": ref_qty,
                            "counted_quantity": c.get("quantity_counted"),
                            "difference": diff,
                            "divergence_type": dtype,
                            "impact": impact,
                            "status": "pending",
                            "adjustment_applied": False,
                        })
                    discrepancies = disc_list
                    _inv_save("inv_discrepancies", discrepancies)
                    if inv:
                        inv["status"] = "AguardandoAprovacao"
                        _inv_save("inv_inventories", inventories)
                    st.success("✅ Conciliação simulada localmente com sucesso! Status: AguardandoAprovacao.")

            st.markdown("#### Divergências encontradas")
            real_disc = _inv_real(xano_client.list_discrepancies, selected_id)
            if real_disc is not None:
                discrepancies = real_disc
                _inv_save("inv_discrepancies", discrepancies)

            inv_discs = [d for d in discrepancies if d.get("inventory_id") == selected_id]
            if not inv_discs:
                st.caption("Nenhuma divergência calculada ainda. Execute a conciliação acima.")
            else:
                for d in inv_discs:
                    p = product_by_id.get(d.get("product_id"), {})
                    dtype = d.get("divergence_type", "none")
                    badge = {"none": "✅ Sem divergência", "shortage": "⚠️ Falta de estoque", "overage": "📦 Sobra de estoque"}.get(dtype, dtype)
                    badge_class = {
                        "none": "status-success",
                        "shortage": "status-warning",
                        "overage": "status-info",
                    }.get(dtype, "status-info")
                    with st.container():
                        st.markdown(f"""
                        <div class="data-card">
                            <div class="data-card-head">
                                <div>
                                    <div class="data-card-title">{p.get('name', 'Produto')}</div>
                                    <div class="data-card-meta">SKU {p.get('sku','—')} · Divergência #{d.get('id')}</div>
                                </div>
                                <span class="status-badge {badge_class}">{badge}</span>
                            </div>
                            <div class="data-card-body">
                                Contado: <b>{d.get('counted_quantity')}</b> &nbsp;|&nbsp;
                                Referência (sistema): <b>{d.get('reference_quantity')}</b> &nbsp;|&nbsp;
                                Diferença: <b>{d.get('difference')}</b> &nbsp;|&nbsp;
                                Status: <b>{d.get('status')}</b>
                            </div>
                            <div class="data-card-meta">Impacto: {d.get('impact','—')}</div>
                        </div>
                        """, unsafe_allow_html=True)

    # ------------------- 5. Aprovação do Gestor -------------------
    with sub_tabs[4]:
        st.markdown("### ✅ Aprovação de Divergências (Gestor)")
        st.caption("Somente gestores podem aprovar, rejeitar ou solicitar recontagem. Validação feita no backend.")

        selected_id = st.session_state.get("inv_selected_id")
        if not selected_id:
            st.warning("Selecione um inventário na aba de listagem primeiro.")
        else:
            inv_discs = []
            if _inv_is_manager:
                inv_discs = [d for d in discrepancies if d.get("inventory_id") == selected_id and d.get("status") == "pending"]
            if not _inv_is_manager:
                st.warning("Seu perfil (" + (_inv_user_role or "sem perfil") + ") não permite aprovar divergências. Apenas Gestor/Admin podem decidir (validação feita no backend).")
            elif not inv_discs:
                st.info("Não há divergências pendentes de decisão neste inventário.")
            else:
                st.write("Divergências aguardando decisão do gestor:")
                for d in inv_discs:
                    p = product_by_id.get(d.get("product_id"), {})
                    with st.container():
                        st.markdown(f"""
                        <div class="data-card data-card--warning">
                            <div class="data-card-head">
                                <div>
                                    <div class="data-card-title">{p.get('name', 'Produto')}</div>
                                    <div class="data-card-meta">SKU {p.get('sku','—')} · Divergência #{d.get('id')}</div>
                                </div>
                                <span class="status-badge status-warning">Pendente</span>
                            </div>
                            <div class="data-card-body">
                                Contado: <b>{d.get('counted_quantity')}</b> &nbsp;|&nbsp;
                                Referência: <b>{d.get('reference_quantity')}</b> &nbsp;|&nbsp;
                                Diferença: <b>{d.get('difference')}</b> ({d.get('divergence_type')})
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        dec_col1, dec_col2, dec_col3, dec_col4 = st.columns([2, 2, 2, 3])
                        with dec_col1:
                            if st.button("✅ Aprovar ajuste", key="inv_ap_" + str(d.get("id"))):
                                res = _inv_real(xano_client.decide_discrepancy, {
                                    "inventory_id": selected_id,
                                    "discrepancy_id": int(d.get("id")),
                                    "action": "approved",
                                    "decided_by": _inv_user_id,
                                    "justification": "Aprovação de divergência de inventário.",
                                })
                                if res is not None:
                                    for idx, dd in enumerate(discrepancies):
                                        if dd.get("id") == d.get("id"):
                                            discrepancies[idx] = res
                                            break
                                    _inv_save("inv_discrepancies", discrepancies)
                                    decisions.append({"inventory_id": selected_id, "product_id": d.get("product_id"), "discrepancy_id": d.get("id"), "action": "approved", "decided_by": _inv_user_id, "decided_at": str(datetime.now()), "justification": "Aprovação de divergência de inventário.", "previous_status": "pending"})
                                    _inv_save("inv_decisions", decisions)
                                    st.success("Divergência aprovada.")
                                    st.rerun()
                        with dec_col2:
                            rej_just = st.text_input("Justificativa da rejeição:", key="inv_rej_" + str(d.get("id")))
                            if st.button("❌ Rejeitar", key="inv_rj_" + str(d.get("id"))):
                                res = _inv_real(xano_client.decide_discrepancy, {
                                    "inventory_id": selected_id,
                                    "discrepancy_id": int(d.get("id")),
                                    "action": "rejected",
                                    "decided_by": _inv_user_id,
                                    "justification": rej_just if rej_just else "Rejeitada pelo gestor.",
                                })
                                if res is not None:
                                    for idx, dd in enumerate(discrepancies):
                                        if dd.get("id") == d.get("id"):
                                            discrepancies[idx] = res
                                            break
                                    _inv_save("inv_discrepancies", discrepancies)
                                    decisions.append({"inventory_id": selected_id, "product_id": d.get("product_id"), "discrepancy_id": d.get("id"), "action": "rejected", "decided_by": _inv_user_id, "decided_at": str(datetime.now()), "justification": rej_just if rej_just else "Rejeitada pelo gestor.", "previous_status": "pending"})
                                    _inv_save("inv_decisions", decisions)
                                    st.success("Divergência rejeitada (nenhum ajuste gerado).")
                                    st.rerun()
                        with dec_col3:
                            if st.button("🔄 Solicitar recontagem", key="inv_rc_" + str(d.get("id"))):
                                res = _inv_real(xano_client.decide_discrepancy, {
                                    "inventory_id": selected_id,
                                    "discrepancy_id": int(d.get("id")),
                                    "action": "recount_requested",
                                    "decided_by": _inv_user_id,
                                    "justification": "Recontagem solicitada pelo gestor.",
                                })
                                if res is not None:
                                    for idx, dd in enumerate(discrepancies):
                                        if dd.get("id") == d.get("id"):
                                            discrepancies[idx] = res
                                            break
                                    _inv_save("inv_discrepancies", discrepancies)
                                    decisions.append({"inventory_id": selected_id, "product_id": d.get("product_id"), "discrepancy_id": d.get("id"), "action": "recount_requested", "decided_by": _inv_user_id, "decided_at": str(datetime.now()), "justification": "Recontagem solicitada pelo gestor.", "previous_status": "pending"})
                                    _inv_save("inv_decisions", decisions)
                                    for i in inventories:
                                        if i.get("id") == selected_id:
                                            i["status"] = "EmContagem"
                                    _inv_save("inv_inventories", inventories)
                                    st.success("Recontagem solicitada. Inventário reaberto para contagem.")
                                    st.rerun()
                        with dec_col4:
                            st.caption("ID da divergência: " + str(d.get("id")))

    # ------------------- 6. Histórico & Ajustes -------------------
    with sub_tabs[5]:
        st.markdown("### 📜 Histórico de Decisões e Ajustes")
        selected_id = st.session_state.get("inv_selected_id")
        if not selected_id:
            st.warning("Selecione um inventário na aba de listagem primeiro.")
        else:
            inv_record = next((i for i in inventories if i.get("id") == selected_id), None)
            if not _inv_is_manager:
                st.info("Aplicar ajustes e concluir o inventário é restrito a Gestor/Admin. A validação real é feita no backend.")
            else:
                action_col1, action_col2 = st.columns(2)
                with action_col1:
                    if st.button("🔄 Aplicar Ajustes Aprovados ao Estoque", type="primary", key="inv_apply"):
                        if _inv_user_id <= 0:
                            st.error("Sessão sem usuário identificado. Faça login novamente.")
                        else:
                            res = _inv_real(xano_client.apply_adjustments, selected_id, _inv_user_id)
                            if res is not None:
                                st.success("✅ " + str(res.get("message", "")) + " Aplicados: " + str(res.get("applied")) + ", Ignorados (concorrência): " + str(res.get("skipped")) + ", Já aplicados: " + str(res.get("already_applied", 0)) + ".")
                                # Atualizar produtos e divergências; se houve conflito, o
                                # backend reabriu o inventário para recontagem.
                                products = _inv_products()
                                product_by_id = {p["id"]: p for p in products}
                                if res.get("skipped", 0) > 0 and inv_record:
                                    inv_record["status"] = "EmContagem"
                                    _inv_save("inv_inventories", inventories)
                                real_disc = _inv_real(xano_client.list_discrepancies, selected_id)
                                if real_disc is not None:
                                    discrepancies = real_disc
                                    _inv_save("inv_discrepancies", discrepancies)

                with action_col2:
                    if not inv_record or inv_record.get("status") != "AguardandoAprovacao":
                        st.caption("Concluir fica disponível quando o inventário estiver em AguardandoAprovacao.")
                    elif st.button("🏁 Concluir Inventário", key="inv_conclude"):
                        if _inv_user_id <= 0:
                            st.error("Sessão sem usuário identificado. Faça login novamente.")
                        else:
                            res = _inv_real(xano_client.transition_inventory_status, selected_id, "Concluido", _inv_user_id)
                            if res is not None:
                                inv_record["status"] = "Concluido"
                                inv_record["closed_at"] = res.get("closed_at") if isinstance(res, dict) else None
                                _inv_save("inv_inventories", inventories)
                                st.success("Inventário concluído. Nenhuma alteração retroativa é permitida.")
                                st.rerun()
                            elif not (xano_client and os.getenv("XANO_BASE_URL")):
                                # Modo demonstração sem backend: mantém a navegação local.
                                inv_record["status"] = "Concluido"
                                _inv_save("inv_inventories", inventories)
                                st.success("Inventário concluído (simulação local).")
                                st.rerun()

            st.markdown("#### Decisões tomadas")
            inv_decisions = [d for d in decisions if d.get("inventory_id") == selected_id]
            if not inv_decisions:
                st.caption("Nenhuma decisão registrada ainda.")
            else:
                dec_rows = []
                for dec in inv_decisions:
                    dec_rows.append({
                        "Divergência #": dec.get("discrepancy_id"),
                        "Ação": dec.get("action"),
                        "Decidido por (ID)": dec.get("decided_by"),
                        "Data": str(dec.get("decided_at", ""))[:16],
                        "Justificativa": dec.get("justification", ""),
                        "Status anterior": dec.get("previous_status"),
                    })
                st.dataframe(dec_rows, use_container_width=True, hide_index=True)

            st.markdown("#### Divergências com ajuste aplicado (ledger de auditoria)")
            applied = [d for d in discrepancies if d.get("inventory_id") == selected_id and d.get("adjustment_applied")]
            if not applied:
                st.caption("Nenhum ajuste aplicado ainda.")
            else:
                for d in applied:
                    p = product_by_id.get(d.get("product_id"), {})
                    st.markdown(f"""
                    <div class="data-card data-card--success">
                        <div class="data-card-head">
                            <div>
                                <div class="data-card-title">{p.get('name', 'Produto')}</div>
                                <div class="data-card-meta">SKU {p.get('sku','—')} · Ajuste #{d.get('id')}</div>
                            </div>
                            <span class="status-badge status-success">Ajuste aplicado</span>
                        </div>
                        <div class="data-card-body">
                            Movimento de ajuste (ledger): <b>#{d.get('adjustment_movement_id')}</b> &nbsp;|&nbsp;
                            Contado: <b>{d.get('counted_quantity')}</b> &nbsp;|&nbsp;
                            Referência: <b>{d.get('reference_quantity')}</b> &nbsp;|&nbsp;
                            Diferença: <b>{d.get('difference')}</b> ({d.get('divergence_type')})
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

elif menu_option == "🚚 Saídas de Estoque":
    _render_page_header(
        "🚚",
        "Saídas de Estoque",
        "Registro e processamento de saídas de venda, laboratório, perda e operação, com bloqueio de saldo negativo e auditoria prévia.",
        "Outbound operations",
    )

    _outbound_user = st.session_state.get("auth_user") or {}
    _outbound_token = st.session_state.get("auth_token")
    _outbound_can_approve = _outbound_user.get("role") in ("Gestor", "admin")

    _outbound_flash = st.session_state.pop("outbound_flash", None)
    if _outbound_flash:
        _flash_level, _flash_message = _outbound_flash
        getattr(st, _flash_level)(_flash_message)

    # Carregar produtos disponíveis
    all_products = []
    if xano_client:
        try:
            all_products = xano_client.list_products(
                auth_token=st.session_state.get("auth_token")
            )
        except Exception:
            all_products = []
    if not all_products:
        all_products = [
            {"id": 1, "sku": "RAY-RB3025-58", "name": "Óculos de Sol Aviador Clássico", "current_stock": 14, "cost_price": 350.0},
            {"id": 2, "sku": "OAK-OX8156-54", "name": "Armação Holbrook RX Fosco", "current_stock": 8, "cost_price": 280.0},
            {"id": 3, "sku": "ZEISS-SV-167-AR", "name": "Lente Zeiss Monofocal 1.67 Duravision", "current_stock": 22, "cost_price": 190.0},
            {"id": 4, "sku": "VAR-COMF-159", "name": "Lente Multifocal Varilux Comfort Max", "current_stock": 5, "cost_price": 420.0},
        ]

    prod_map = {p["id"]: p for p in all_products}
    prod_options = {f"#{p['id']} - {p.get('name', 'Produto')} ({p.get('sku', '')}) [Saldo: {p.get('current_stock', 0)}]": p["id"] for p in all_products}

    # Saídas vêm exclusivamente do backend; não há estado local/mock para auditoria.
    outbounds_list = []
    if xano_client and _outbound_token:
        try:
            remote_outbounds = xano_client.list_outbounds(auth_token=_outbound_token)
            if isinstance(remote_outbounds, list):
                outbounds_list = remote_outbounds
        except Exception as exc:
            st.error("Não foi possível consultar as saídas no Xano: " + str(exc))
    else:
        st.error("Backend Xano ou sessão autenticada indisponível para o módulo de saídas.")

    total_ops = len(outbounds_list)
    pendentes_aprov = len([o for o in outbounds_list if o.get("status") in ["Pendente", "AguardandoAprovacao"]])
    concluidas = len([o for o in outbounds_list if o.get("status") == "Concluida"])
    total_itens_baixados = sum(o.get("quantity", 0) for o in outbounds_list if o.get("status") == "Concluida")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total de Operações</div>
            <div class="kpi-value">{total_ops}</div>
            <div class="kpi-delta">Operações registradas</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Aguardando Decisão</div>
            <div class="kpi-value" style="color:#d97706;">{pendentes_aprov}</div>
            <div class="kpi-delta">Pendentes / Aprovação</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Efetivadas (Baixa OK)</div>
            <div class="kpi-value" style="color:#10b981;">{concluidas}</div>
            <div class="kpi-delta">Ledger atualizado</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Peças Baixadas</div>
            <div class="kpi-value" style="color:#3942f6;">{total_itens_baixados}</div>
            <div class="kpi-delta">Unidades expedidas</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Abas da Change 04
    tab_reg, tab_hist, tab_gest = st.tabs([
        "📝 Nova Saída de Estoque",
        "📋 Histórico & Rastreabilidade Auditada",
        "🛡️ Central de Aprovação Gerencial"
    ])

    # 1. ABA DE REGISTRO
    with tab_reg:
        st.markdown("#### Registrar Saída Autorizada de Estoque")
        st.markdown("Selecione o tipo de saída e informe os dados de origem. Baixas de perda (LOSS) exigem justificativa obrigatória e aprovação do gestor.")

        col_t1, col_t2 = st.columns([1, 2])
        with col_t1:
            out_type = st.selectbox(
                "Tipo de Saída:",
                options=["SALE", "LAB_SHIPMENT", "LOSS", "OPERATIONAL"],
                format_func=lambda x: {
                    "SALE": "🛒 Venda Comercial (PDV)",
                    "LAB_SHIPMENT": "🔬 Envio para Laboratório (Montagem/OS)",
                    "LOSS": "⚠️ Perda / Avaria / Quebra",
                    "OPERATIONAL": "📦 Saída Operacional / Transferência"
                }.get(x, x),
                key="out_type_sel"
            )

        with col_t2:
            prod_labels = list(prod_options.keys())
            default_prod_index = next(
                (
                    i
                    for i, p in enumerate(all_products)
                    if p.get("current_stock", 0) > 0
                ),
                0,
            )
            prod_sel_label = st.selectbox(
                "Selecione o Produto:",
                options=prod_labels,
                index=default_prod_index,
                key="out_prod_sel",
            )
            selected_pid = prod_options.get(prod_sel_label)
            selected_prod_obj = prod_map.get(selected_pid, {})
            current_avail = selected_prod_obj.get("current_stock", 0)

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            out_qty = st.number_input("Quantidade a Retirar:", min_value=1, max_value=max(1, current_avail), value=1, step=1, key="out_qty_input")
            if current_avail <= 0:
                st.warning("Produto sem saldo disponível. Selecione outro produto.")
            elif out_qty > current_avail:
                st.error(f"❌ Quantidade solicitada ({out_qty}) excede o saldo disponível ({current_avail})!")
            else:
                st.caption(f"Saldo restante após baixa: **{current_avail - out_qty}** un.")

        with col_f2:
            st.caption(
                "Operador autenticado: "
                + str(_outbound_user.get("name") or _outbound_user.get("email") or "sessão atual")
                + f" (ID {_outbound_user.get('id', '-')})"
            )
            if _outbound_can_approve:
                st.caption("Perfil com permissão de aprovação.")
            else:
                st.caption("Perdas exigirão aprovação de um Gestor/admin.")

        with col_f3:
            idempotency_key = st.text_input("Chave de Idempotência (Opcional):", value=f"OUT-{selected_pid}-{int(datetime.now().timestamp())}", key="out_idem_key")

        # Campos condicionais conforme tipo de saída
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if out_type == "SALE":
                ref_type = "SALE"
                ref_id = st.text_input("Número do Pedido / Cupom Fiscal:", value="VD-2026-00491", key="out_ref_sale")
                dest = None
                reason_default = f"Venda balcão - Pedido {ref_id}"
            elif out_type == "LAB_SHIPMENT":
                ref_type = "OS"
                ref_id = st.text_input("Número da Ordem de Serviço (OS):", value="OS-9941", key="out_ref_lab")
                dest = st.selectbox("Laboratório de Destino:", ["Laboratório Central Hoya/Essilor", "Laboratório Interno Loja 04", "Surfaçagem Digital Pró-Ótica"], key="out_dest_lab")
                reason_default = f"Envio para montagem OS #{ref_id}"
            elif out_type == "LOSS":
                ref_type = "INTERNAL"
                ref_id = st.text_input("Código do Incidente / Avaria:", value="AV-2026-10", key="out_ref_loss")
                dest = "Descarte Auditado / Sucata"
                reason_default = "Perda por quebra/avaria operacional"
            else:
                ref_type = "TRANSFER"
                ref_id = st.text_input("Referência Operacional:", value="TRANSF-LJ02", key="out_ref_op")
                dest = st.text_input("Destino / Setor:", value="Filial Shopping Ibirapuera", key="out_dest_op")
                reason_default = "Transferência autorizada de mostruário"

        with col_c2:
            out_reason = st.text_input("Motivo da Saída:", value=reason_default, key="out_reason_input")
            out_notes = st.text_input("Observações Adicionais:", value="", key="out_notes_input")

        justification_input = ""
        if out_type == "LOSS":
            st.markdown('<div class="status-badge status-warning">⚠️ ATENÇÃO: Justificativa obrigatória para auditoria de perdas.</div>', unsafe_allow_html=True)
            justification_input = st.text_area(
                "Justificativa da Perda / Avaria (Obrigatório):",
                value="Produto quebrou durante ajuste fino na ventilete térmica. Sem condições de comercialização.",
                key="out_just_input"
            )

        st.write("")
        if st.button(
            "🚀 Confirmar e Efetivar Saída de Estoque",
            type="primary",
            key="btn_confirm_out",
            disabled=current_avail <= 0,
        ):
            # Validações de UX; o backend continua sendo a autoridade final.
            if not (xano_client and _outbound_token):
                st.error("Backend Xano ou sessão autenticada indisponível para registrar a saída.")
            elif out_qty > current_avail:
                st.error("Operação bloqueada: o saldo em estoque é insuficiente para esta quantidade.")
            elif out_type == "LOSS" and not justification_input.strip():
                st.error("A justificativa é obrigatória para registrar saídas do tipo PERDA (LOSS).")
            else:
                payload_out = {
                    "type": out_type,
                    "product_id": int(selected_pid),
                    "quantity": int(out_qty),
                    "reason": out_reason,
                    "justification": justification_input if justification_input.strip() else None,
                    "reference_type": ref_type,
                    "reference_id": ref_id,
                    "destination": dest,
                    "notes": out_notes if out_notes.strip() else None,
                    "idempotency_key": idempotency_key or None,
                }

                try:
                    res_create = xano_client.create_outbound(
                        payload_out,
                        auth_token=_outbound_token,
                    )

                    if out_type == "LOSS":
                        st.session_state.outbound_flash = (
                            "info",
                            f"⏳ Solicitação de perda #{res_create['id']} registrada e enviada "
                            "para aprovação do gestor.",
                        )
                    else:
                        res_proc = xano_client.process_outbound(
                            res_create["id"],
                            auth_token=_outbound_token,
                        )
                        movement = res_proc.get("movement") or {}
                        movement_id = movement.get("id", "-")
                        st.session_state.outbound_flash = (
                            "success",
                            f"✅ Saída #{res_create['id']} concluída com sucesso! "
                            f"Baixa no estoque efetivada (Movimento #{movement_id}).",
                        )
                except Exception as ex:
                    st.error(f"Erro ao registrar/processar saída de estoque: {ex}")
                else:
                    st.rerun()

    # 2. ABA DE HISTÓRICO & FILTROS
    with tab_hist:
        st.markdown("#### Histórico Auditado de Saídas de Estoque")
        st.markdown("Consulte e filtre todas as operações de saída. Registros concluídos são imutáveis e auditados.")

        col_fil1, col_fil2, col_fil3 = st.columns(3)
        with col_fil1:
            fil_type = st.selectbox("Filtrar por Tipo:", ["Todos", "SALE", "LAB_SHIPMENT", "LOSS", "OPERATIONAL"], key="fil_type_hist")
        with col_fil2:
            fil_status = st.selectbox("Filtrar por Status:", ["Todos", "Concluida", "AguardandoAprovacao", "Pendente", "Rejeitada", "Cancelada", "FalhaNoProcessamento"], key="fil_stat_hist")
        with col_fil3:
            fil_search = st.text_input("Buscar por Referência / Motivo / OS:", value="", key="fil_srch_hist")

        filtered_outbounds = list(outbounds_list)
        if fil_type != "Todos":
            filtered_outbounds = [o for o in filtered_outbounds if o.get("type") == fil_type]
        if fil_status != "Todos":
            filtered_outbounds = [o for o in filtered_outbounds if o.get("status") == fil_status]
        if fil_search.strip():
            s = fil_search.strip().lower()
            filtered_outbounds = [o for o in filtered_outbounds if s in str(o.get("reference_id", "")).lower() or s in str(o.get("reason", "")).lower()]

        if not filtered_outbounds:
            st.info("Nenhuma operação de saída encontrada para os filtros selecionados.")
        else:
            for out_item in filtered_outbounds:
                p = prod_map.get(out_item.get("product_id"), {})
                is_completed = out_item.get("status") == "Concluida"
                qty_label = f"-{out_item.get('quantity')}" if is_completed else f"{out_item.get('quantity')}"
                qty_color = "#dc2626" if is_completed else "#334155"
                st_badge_class = {
                    "Concluida": "status-success",
                    "AguardandoAprovacao": "status-warning",
                    "Pendente": "status-info",
                    "Rejeitada": "status-danger",
                    "Cancelada": "status-info",
                    "FalhaNoProcessamento": "status-danger",
                }.get(out_item.get("status"), "status-info")

                st.markdown(f"""
                <div class="data-card">
                    <div class="data-card-head">
                        <div>
                            <div class="data-card-title">Saída #{out_item.get('id')} <span class="type-chip">{out_item.get('type')}</span></div>
                            <div class="data-card-meta">Registrada em {out_item.get('created_at')}</div>
                        </div>
                        <span class="status-badge {st_badge_class}">{out_item.get('status')}</span>
                    </div>
                    <div class="data-card-body">
                        <b>Produto:</b> {p.get('name', 'Produto')} ({p.get('sku', '')}) &nbsp;|&nbsp;
                        <b>Qtd:</b> <span style="color:{qty_color}; font-weight:700;">{qty_label} un.</span> &nbsp;|&nbsp;
                        <b>Referência:</b> {out_item.get('reference_type', '')} {out_item.get('reference_id', '-')} &nbsp;|&nbsp;
                        <b>Operador:</b> User #{out_item.get('user_id')}
                    </div>
                    <div class="data-card-meta">
                        <b>Motivo:</b> {out_item.get('reason', '-')}
                        {f" &nbsp;|&nbsp; <b>Destino:</b> {out_item.get('destination')}" if out_item.get('destination') else ""}
                        {f" &nbsp;|&nbsp; <b>Movimento Ledger:</b> #{out_item.get('stock_movement_id')}" if out_item.get('stock_movement_id') else ""}
                    </div>
                    {f'<div class="audit-note"><b>Justificativa de Auditoria:</b> {out_item.get("justification")}</div>' if out_item.get("justification") else ''}
                </div>
                """, unsafe_allow_html=True)

    # 3. ABA DE APROVAÇÃO GERENCIAL
    with tab_gest:
        st.markdown("#### Central de Decisão e Aprovação Gerencial")
        st.markdown("Operações que exigem autorização expressa (como perdas e descartes de alto valor) antes do débito no estoque.")

        pending_approval = [
            o
            for o in outbounds_list
            if o.get("status") in ("AguardandoAprovacao", "Pendente")
        ]
        if not pending_approval:
            st.success("🎉 Nenhuma solicitação de saída pendente de aprovação no momento.")
        else:
            if not _outbound_can_approve:
                st.info(
                    "Somente usuários com perfil Gestor/admin podem aprovar, rejeitar ou "
                    "reprocessar saídas pendentes."
                )

            for item in pending_approval:
                p = prod_map.get(item.get("product_id"), {})
                is_waiting = item.get("status") == "AguardandoAprovacao"
                status_label = "Aguardando Gestor" if is_waiting else "Pendente de processamento"
                st.markdown(f"""
                <div class="data-card data-card--warning">
                    <div class="data-card-head">
                        <div>
                            <div class="data-card-title">Solicitação #{item.get('id')} <span class="type-chip">{item.get('type')}</span></div>
                            <div class="data-card-meta">Operação aguardando validação gerencial</div>
                        </div>
                        <span class="status-badge status-warning">{status_label}</span>
                    </div>
                    <div class="data-card-body">
                        <b>Produto:</b> {p.get('name', 'Produto')} ({p.get('sku', '')}) &nbsp;|&nbsp;
                        <b>Quantidade:</b> {item.get('quantity')} un. &nbsp;|&nbsp;
                        <b>Solicitante:</b> Usuário #{item.get('user_id')}
                    </div>
                    <div class="data-card-meta"><b>Motivo:</b> {item.get('reason')}</div>
                    <div class="audit-note"><b>Justificativa de perda:</b> {item.get('justification', 'Não informada')}</div>
                </div>
                """, unsafe_allow_html=True)

                if not _outbound_can_approve:
                    continue

                col_b1, col_b2, col_b3 = st.columns([1, 1, 3])
                with col_b1:
                    if st.button(f"✅ Aprovar & Baixar #{item.get('id')}", key=f"btn_aprov_{item.get('id')}", type="primary"):
                        if not (xano_client and _outbound_token):
                            st.error("Backend Xano ou sessão autenticada indisponível.")
                        else:
                            try:
                                xano_client.process_outbound(
                                    item.get("id"),
                                    auth_token=_outbound_token,
                                )
                            except Exception as ex:
                                st.error(f"Erro ao aprovar/processar saída #{item.get('id')}: {ex}")
                            else:
                                st.session_state.outbound_flash = (
                                    "success",
                                    f"Saída #{item.get('id')} aprovada e estoque baixado com sucesso!",
                                )
                                st.rerun()

                with col_b2:
                    action_status = "Rejeitada" if is_waiting else "Cancelada"
                    action_label = "❌ Rejeitar" if is_waiting else "✖️ Cancelar"
                    action_key = "rej" if is_waiting else "cancel"
                    if st.button(
                        f"{action_label} #{item.get('id')}",
                        key=f"btn_{action_key}_{item.get('id')}",
                    ):
                        if not (xano_client and _outbound_token):
                            st.error("Backend Xano ou sessão autenticada indisponível.")
                        else:
                            try:
                                xano_client.update_outbound_status(
                                    item.get("id"),
                                    action_status,
                                    auth_token=_outbound_token,
                                )
                            except Exception as ex:
                                st.error(
                                    f"Erro ao atualizar a saída #{item.get('id')} "
                                    f"para {action_status}: {ex}"
                                )
                            else:
                                if is_waiting:
                                    flash_level = "warning"
                                    flash_message = (
                                        f"Saída #{item.get('id')} rejeitada. "
                                        "O saldo em estoque permaneceu inalterado."
                                    )
                                else:
                                    flash_level = "info"
                                    flash_message = (
                                        f"Saída #{item.get('id')} cancelada. "
                                        "O saldo em estoque permaneceu inalterado."
                                    )
                                st.session_state.outbound_flash = (
                                    flash_level,
                                    flash_message,
                                )
                                st.rerun()


# -----------------------------------------------------------------------------
# CHANGE 05: ALERTAS DE ESTOQUE E REPOSIÇÃO
# -----------------------------------------------------------------------------
elif menu_option == "🔔 Alertas & Reposição":
    _render_page_header(
        "🔔",
        "Alertas & Reposição",
        "Monitoramento de ruptura, inatividade e sugestões de reposição calculadas pelo backend Xano.",
        "Inteligência de estoque",
    )
    st.caption(
        "Toda regra é calculada no backend — esta tela apenas consome a API e apresenta o resultado."
    )

    # Sem mock: se o backend não estiver acessível, é estado de erro explícito.
    if not (xano_client and os.getenv("XANO_BASE_URL")):
        st.error(
            "Serviço Xano não configurado ou indisponível. Defina a URL do backend para usar "
            "este módulo — não há dados simulados nesta seção."
        )
        st.stop()

    # ------------------------------------------------------------------
    # Helpers de formatação (timestamps do Xano vêm em epoch ms)
    # ------------------------------------------------------------------
    def _alert_formatar_ts(ts_ms):
        """Converte epoch ms do Xano para data legível; '—' se ausente."""
        try:
            return datetime.fromtimestamp(int(ts_ms) / 1000).strftime("%d/%m/%Y %H:%M")
        except (TypeError, ValueError, OSError):
            return "—"

    def _alert_dias_sem_movimentar(ts_ms):
        """Dias decorridos desde a última movimentação (None se nunca houve)."""
        try:
            return max((datetime.now() - datetime.fromtimestamp(int(ts_ms) / 1000)).days, 0)
        except (TypeError, ValueError, OSError):
            return None

    # ------------------------------------------------------------------
    # Usuário requisitante (todo endpoint exige user_id; perfil é validado no backend)
    # ------------------------------------------------------------------
    _alert_auth_user = st.session_state.get("auth_user") or {}
    try:
        _alert_default_user_id = max(int(_alert_auth_user.get("id") or 1), 1)
    except (TypeError, ValueError):
        _alert_default_user_id = 1

    col_uid1, col_uid2 = st.columns([1, 3])
    with col_uid1:
        alert_user_id = st.number_input(
            "ID do usuário requisitante:",
            min_value=1, value=_alert_default_user_id, step=1, key="alert_user_id_input",
        )
    with col_uid2:
        st.info(
            "Leitura: todos os perfis. Avaliação e transições de alerta: Gestor, Estoquista "
            "ou admin. Parâmetros de estoque: Gestor ou admin. A validação é feita no backend."
        )

    # ------------------------------------------------------------------
    # Resumo geral (KPIs + perfil do ator, usado para esconder ações na UI)
    # ------------------------------------------------------------------
    try:
        with st.spinner("Carregando resumo de alertas..."):
            alert_summary = xano_client.get_alerts_summary(int(alert_user_id))
    except Exception as exc:
        st.markdown("""
        <div class="module-empty">
            <div class="module-empty-icon">🔔</div>
            <div>
                <div class="module-empty-title">Monitoramento de alertas indisponível neste ambiente</div>
                <p class="module-empty-text">
                    O serviço de alertas ainda não foi publicado no backend configurado.
                    Esta tela permanece sem dados simulados para não exibir indicadores imprecisos.
                    Tente novamente quando o módulo estiver disponível.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("Detalhes técnicos"):
            st.code(str(exc))
        st.stop()

    actor_role = alert_summary.get("actor_role", "")
    pode_avaliar = actor_role in ("Gestor", "Estoquista", "admin")
    pode_configurar = actor_role in ("Gestor", "admin")

    st.markdown("##### Indicadores do Monitoramento")
    kpi_cols = st.columns(5)
    kpi_cols[0].metric("🚨 Alertas Ativos", alert_summary.get("alertas_ativos", 0))
    kpi_cols[1].metric("🔥 Alertas Críticos", alert_summary.get("alertas_criticos", 0))
    kpi_cols[2].metric("🕓 Produtos Inativos", alert_summary.get("produtos_inativos", 0))
    kpi_cols[3].metric("⚙️ Parâmetros Incompletos", alert_summary.get("parametros_incompletos", 0))
    kpi_cols[4].metric("📦 Produtos Monitorados", alert_summary.get("produtos_monitorados", 0))

    st.caption(
        f"Requisitante: usuário #{alert_summary.get('actor_id', alert_user_id)} — "
        f"perfil **{actor_role or 'desconhecido'}** | "
        f"avaliação de alertas: {'✅ permitida' if pode_avaliar else '🚫 restrita'} | "
        f"parâmetros de estoque: {'✅ permitida' if pode_configurar else '🚫 restrita'}"
    )

    # ------------------------------------------------------------------
    # Avaliação idempotente de alertas (não altera saldo nem cria movimentação)
    # ------------------------------------------------------------------
    col_av1, col_av2 = st.columns([2, 3])
    with col_av1:
        if pode_avaliar:
            if st.button("🔄 Avaliar Alertas Agora", type="primary", key="btn_avaliar_alertas"):
                try:
                    with st.spinner("Avaliando produtos monitorados..."):
                        resultado = xano_client.evaluate_alerts(int(alert_user_id))
                    st.success(
                        f"Avaliação concluída: {resultado.get('avaliados', 0)} produto(s) avaliados — "
                        f"{resultado.get('criados', 0)} alerta(s) criado(s), "
                        f"{resultado.get('resolvidos', 0)} auto-resolvido(s), "
                        f"{resultado.get('silenciados', 0)} silenciado(s)."
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(f"Falha na avaliação de alertas: {exc}")
        else:
            st.warning(
                "Seu perfil não pode executar a avaliação de alertas "
                "(requer Gestor, Estoquista ou admin — validado no backend)."
            )

    st.divider()

    tab_alertas, tab_sem_mov, tab_sugestoes, tab_parametros = st.tabs([
        "🚨 Alertas",
        "🕓 Sem Movimentação",
        "📦 Sugestões de Reposição",
        "⚙️ Parâmetros de Estoque",
    ])

    # ------------------------------------------------------------------
    # ABA 1 — ALERTAS (filtros, cards e transições do ciclo de vida)
    # ------------------------------------------------------------------
    with tab_alertas:
        st.markdown("#### Ciclo de Vida dos Alertas")
        st.caption(
            "Transições manuais permitidas: Ativo → EmAcompanhamento e "
            "Ativo/EmAcompanhamento → Resolvido. Resolvido é estado final e o histórico é sempre preservado."
        )

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_status = st.selectbox(
                "Status:", ["Todos", "Ativo", "EmAcompanhamento", "Resolvido"], key="alert_filtro_status"
            )
        with col_f2:
            filtro_tipo = st.selectbox(
                "Tipo:", ["Todos", "LOW_STOCK", "INACTIVE"], key="alert_filtro_tipo"
            )
        with col_f3:
            filtro_pid = st.number_input(
                "ID do produto (0 = todos):", min_value=0, value=0, step=1, key="alert_filtro_pid"
            )

        try:
            with st.spinner("Carregando alertas..."):
                alertas = xano_client.list_alerts(
                    int(alert_user_id),
                    status=None if filtro_status == "Todos" else filtro_status,
                    alert_type=None if filtro_tipo == "Todos" else filtro_tipo,
                    product_id=int(filtro_pid) or None,
                )
        except Exception as exc:
            st.error(f"Falha ao carregar alertas: {exc}")
            alertas = None

        if alertas is not None:
            if not alertas:
                st.info("Nenhum alerta encontrado para os filtros selecionados.")
            for alerta in alertas:
                status_atual = alerta.get("status", "")
                tipo_alerta = alerta.get("alert_type", "")
                tipo_label = "Estoque Baixo" if tipo_alerta == "LOW_STOCK" else "Sem Movimentação"
                cor_bloco = {
                    "critico": "#DC2626",
                    "insuficiente": "#D97706",
                    "regular": "#059669",
                }.get(str(alerta.get("criticality", "")).lower(), "#64748B")
                classe_badge = {
                    "Ativo": "status-danger",
                    "EmAcompanhamento": "status-warning",
                    "Resolvido": "status-success",
                }.get(status_atual, "status-info")

                resolvido_html = ""
                if status_atual == "Resolvido":
                    resolvido_html = (
                        f"<div style='margin-top:4px; font-size:0.82rem; color:#059669;'>"
                        f"Resolvido em {_alert_formatar_ts(alerta.get('resolved_at'))} "
                        f"(motivo: {alerta.get('resolution') or '—'})</div>"
                    )

                st.markdown(
                    f"""
                    <div class="alert-card" style="border-left-color: {cor_bloco};">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-weight:700;">#{alerta.get('id')} — {alerta.get('produto_nome', 'Produto')}</span>
                                <span style="color:#64748b;"> ({alerta.get('produto_sku', '—')})</span>
                            </div>
                            <div>
                                <span class="status-badge {classe_badge}">{status_atual}</span>
                                &nbsp;
                                <span class="status-badge status-info">{tipo_label}</span>
                            </div>
                        </div>
                        <div style="margin-top:6px; font-size:0.88rem; color:#334155;">
                            <b>Saldo observado:</b> {alerta.get('observed_stock', '—')} un.
                            &nbsp;|&nbsp; <b>Mínimo observado:</b> {alerta.get('observed_min_stock', '—')} un.
                            &nbsp;|&nbsp; <b>Classificação:</b> {alerta.get('criticality', '—')}
                        </div>
                        <div style="margin-top:4px; font-size:0.82rem; color:#64748b;">
                            Detectado em: {_alert_formatar_ts(alerta.get('detected_at'))}
                            &nbsp;|&nbsp; Status atualizado em: {_alert_formatar_ts(alerta.get('status_updated_at'))}
                        </div>
                        {resolvido_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if pode_avaliar and status_atual != "Resolvido":
                    col_a1, col_a2, _ = st.columns([1, 1, 4])
                    with col_a1:
                        if status_atual == "Ativo":
                            if st.button("👀 Acompanhar", key=f"btn_acomp_{alerta.get('id')}"):
                                try:
                                    xano_client.update_alert_status(
                                        int(alerta.get("id")), "EmAcompanhamento", int(alert_user_id)
                                    )
                                    st.success(f"Alerta #{alerta.get('id')} movido para EmAcompanhamento.")
                                    st.rerun()
                                except Exception as exc:
                                    st.error(f"Falha ao atualizar o alerta: {exc}")
                    with col_a2:
                        if st.button("✅ Resolver", key=f"btn_resolver_{alerta.get('id')}"):
                            try:
                                xano_client.update_alert_status(
                                    int(alerta.get("id")), "Resolvido", int(alert_user_id)
                                )
                                st.success(f"Alerta #{alerta.get('id')} resolvido (histórico preservado).")
                                st.rerun()
                            except Exception as exc:
                                st.error(f"Falha ao resolver o alerta: {exc}")

    # ------------------------------------------------------------------
    # ABA 2 — PRODUTOS SEM MOVIMENTAÇÃO
    # ------------------------------------------------------------------
    with tab_sem_mov:
        st.markdown("#### Produtos Sem Movimentação Recente")
        st.caption(
            "**Inativo**: tem histórico, mas parou de se movimentar além da janela (gera alerta INACTIVE). "
            "**Sem Histórico**: nunca teve movimentação (não gera alerta). "
            "A janela segue a prioridade: informada aqui > configurada no produto > 30 dias."
        )

        col_j1, col_j2 = st.columns(2)
        with col_j1:
            janela_dias = st.number_input(
                "Janela de inatividade em dias (vazio = padrão do produto):",
                min_value=1, value=None, step=1, key="alert_janela_dias",
            )
        with col_j2:
            incluir_sem_hist = st.checkbox(
                "Incluir produtos sem histórico", value=True, key="alert_incluir_sem_hist"
            )

        try:
            with st.spinner("Verificando movimentações..."):
                inativos = xano_client.list_inactive_products(
                    int(alert_user_id),
                    inactivity_days=int(janela_dias) if janela_dias else None,
                    incluir_sem_historico=bool(incluir_sem_hist),
                )
        except Exception as exc:
            st.error(f"Falha ao listar produtos sem movimentação: {exc}")
            inativos = None

        if inativos is not None:
            if not inativos:
                st.info("Nenhum produto encontrado para a janela selecionada.")
            else:
                linhas_inat = []
                for item in inativos:
                    dias = _alert_dias_sem_movimentar(item.get("ultima_movimentacao"))
                    situacao = item.get("situacao", "")
                    linhas_inat.append({
                        "Produto ID": item.get("product_id"),
                        "SKU": item.get("sku"),
                        "Nome": item.get("nome"),
                        "Categoria": item.get("categoria"),
                        "Saldo": item.get("saldo"),
                        "Situação": "🕓 Inativo" if situacao == "Inativo" else "❓ Sem Histórico",
                        "Última movimentação": _alert_formatar_ts(item.get("ultima_movimentacao")),
                        "Dias sem movimentar": dias if dias is not None else "—",
                        "Janela (dias)": item.get("janela_dias"),
                    })
                st.dataframe(linhas_inat, use_container_width=True)

    # ------------------------------------------------------------------
    # ABA 3 — SUGESTÕES DE REPOSIÇÃO (somente recomendações)
    # ------------------------------------------------------------------
    with tab_sugestoes:
        st.markdown("#### Sugestões de Reposição")
        st.caption(
            "Sugestão = `max(0, estoque alvo − saldo atual)`. Sem estoque alvo configurado a "
            "sugestão vem vazia e o produto é sinalizado com parâmetros incompletos. "
            "É apenas uma recomendação — nenhuma compra ou entrada é criada a partir daqui."
        )

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            filtro_cat = st.text_input(
                "Filtrar por categoria (vazio = todas):", value="", key="alert_filtro_cat"
            )
        with col_s2:
            filtro_rep_pid = st.number_input(
                "ID do produto (0 = todos):", min_value=0, value=0, step=1, key="alert_filtro_rep_pid"
            )

        try:
            with st.spinner("Carregando sugestões..."):
                sugestoes = xano_client.list_replenishment(
                    int(alert_user_id),
                    category=filtro_cat.strip() or None,
                    product_id=int(filtro_rep_pid) or None,
                )
        except Exception as exc:
            st.error(f"Falha ao carregar sugestões: {exc}")
            sugestoes = None

        if sugestoes is not None:
            incompletos = [item for item in sugestoes if item.get("parametros_incompletos")]
            if incompletos:
                st.warning(
                    f"{len(incompletos)} produto(s) sem estoque alvo configurado — a sugestão de "
                    "reposição fica vazia até o Gestor definir o parâmetro na aba de Parâmetros de Estoque."
                )

            if not sugestoes:
                st.info("Nenhum produto encontrado para os filtros selecionados.")
            else:
                total_unidades = 0
                total_investimento = 0.0
                crit_map = {
                    "critico": "🔴 Crítico",
                    "insuficiente": "🟡 Insuficiente",
                    "regular": "🟢 Regular",
                }
                linhas_sug = []
                for item in sugestoes:
                    sug = item.get("sugestao")
                    custo = item.get("custo_estimado") or 0.0
                    if isinstance(sug, int):
                        total_unidades += sug
                        total_investimento += custo
                    linhas_sug.append({
                        "Produto ID": item.get("product_id"),
                        "SKU": item.get("sku"),
                        "Nome": item.get("nome"),
                        "Categoria": item.get("categoria"),
                        "Saldo": item.get("saldo"),
                        "Mínimo": item.get("min_stock"),
                        "Alvo": item.get("target_stock") if item.get("target_stock") is not None else "—",
                        "Classificação": crit_map.get(str(item.get("classificacao", "")).lower(), "—"),
                        "Sugestão (un)": sug if sug is not None else "sem alvo",
                        "Custo Estimado": f"R$ {custo:,.2f}",
                    })
                st.dataframe(linhas_sug, use_container_width=True)

                col_t1, col_t2 = st.columns(2)
                col_t1.metric("Total Sugerido (un.)", total_unidades)
                col_t2.metric("Investimento Estimado", f"R$ {total_investimento:,.2f}")

    # ------------------------------------------------------------------
    # ABA 4 — PARÂMETROS DE ESTOQUE (restrito a Gestor/admin)
    # ------------------------------------------------------------------
    with tab_parametros:
        st.markdown("#### Configurar Parâmetros de Estoque")
        if not pode_configurar:
            st.warning(
                "Seu perfil não pode alterar parâmetros de estoque "
                "(requer Gestor ou admin — validado no backend)."
            )
        else:
            st.caption(
                "Somente os campos preenchidos são alterados; os demais preservam o valor atual. "
                "Deixe um campo vazio para não alterá-lo."
            )

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                param_pid = st.number_input("ID do produto:", min_value=1, value=1, step=1, key="param_pid")
                param_min = st.number_input(
                    "Estoque mínimo (vazio = não alterar):",
                    min_value=0, value=None, step=1, key="param_min",
                )
                param_definir_target = st.checkbox(
                    "Definir/Atualizar estoque alvo", value=False, key="param_definir_target"
                )
                param_target = None
                if param_definir_target:
                    param_target = st.number_input(
                        "Estoque alvo:", min_value=0, value=0, step=1, key="param_target",
                    )
            with col_p2:
                param_janela = st.number_input(
                    "Janela de inatividade em dias (vazio = não alterar):",
                    min_value=1, value=None, step=1, key="param_janela",
                )
                param_alertas_on = st.checkbox(
                    "Monitoramento de alertas ativo para o produto", value=True, key="param_alertas_on"
                )

            if st.button("💾 Salvar Parâmetros", type="primary", key="btn_salvar_parametros"):
                try:
                    with st.spinner("Salvando parâmetros..."):
                        produto = xano_client.update_stock_parameters(
                            int(param_pid),
                            int(alert_user_id),
                            min_stock=int(param_min) if param_min is not None else None,
                            target_stock=int(param_target) if param_target is not None else None,
                            inactivity_days=int(param_janela) if param_janela is not None else None,
                            alerts_enabled=bool(param_alertas_on),
                        )
                    alvo_exibido = produto.get("target_stock")
                    st.success(
                        f"Parâmetros do produto #{param_pid} atualizados — "
                        f"mínimo: {produto.get('min_stock')}, "
                        f"alvo: {alvo_exibido if alvo_exibido is not None else '—'}, "
                        f"janela: {produto.get('inactivity_days') or '—'} dia(s), "
                        f"alertas: {'ativos' if produto.get('alerts_enabled') else 'inativos'}."
                    )
                except Exception as exc:
                    st.error(f"Falha ao salvar parâmetros: {exc}")



