---
name: streamlit-design-system
description: Diretrizes de UI/UX, Design System, CSS customizado e componentes visuais premium para interfaces Streamlit modernas e profissionais (cards, métricas, cabeçalhos, formulários, tabelas e tipografia).
---

# Streamlit Design System & UI Guidelines

Este guia estabelece os padrões visuais, tokens de design, componentes reutilizáveis e regras de injeção de CSS para transformar aplicações Streamlit em interfaces modernas, elegantes e com sensação de produto SaaS de alto padrão ("Rich Aesthetics").

---

## 1. Tokens de Design & Identidade Visual

### Paleta de Cores
A identidade padrão baseia-se no branding corporativo moderno com alto contraste e harmonia:

| Token | Hex / Valor | Uso |
| :--- | :--- | :--- |
| `--primary` | `#3942F6` | Botões principais, links, destaques ativos, headers |
| `--primary-hover` | `#252CD6` | Estado de hover em elementos primários |
| `--primary-light` | `rgba(57, 66, 246, 0.08)` | Fundos de cards ativos, tags suaves |
| `--secondary` | `#F8B807` | Alertas dourados, destaques de valor, estrelas/metas |
| `--bg-main` | `#F1F2F4` ou `#F8FAFC` | Fundo geral da aplicação |
| `--card-bg` | `#FFFFFF` | Superfície de cards, modais e containers |
| `--border-color` | `#E2E8F0` | Bordas sutis de separação e contornos |
| `--border-focus` | `#3942F6` | Anel de foco para inputs e seleção |
| `--text-main` | `#0F172A` | Títulos e textos de alta ênfase |
| `--text-muted` | `#64748B` | Subtítulos, labels secundárias, metadados |
| `--success` | `#10B981` | Metas batidas, status ativo, sucesso |
| `--warning` | `#F59E0B` | Atenção, prazos próximos |
| `--danger` | `#EF4444` | Falhas, bloqueios, metas críticas abaixo do esperado |

### Tipografia & Espaçamento
- **Fonte Principal:** `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Tamanhos:**
  - Hero / Título Principal: `1.8rem - 2.2rem`, peso `700` ou `800`, letter-spacing `-0.5px`
  - Seções / H2: `1.25rem - 1.4rem`, peso `600`
  - Cards / H3: `1.05rem - 1.15rem`, peso `600`
  - Corpo / Body: `0.9rem - 0.95rem`, peso `400`
  - Legendas / Micro: `0.75rem - 0.8rem`, peso `500`
- **Raios de Borda (`border-radius`):**
  - Botões & Inputs: `8px` a `10px`
  - Cards & Containers: `12px` a `16px`
  - Badges & Pills: `9999px` (totalmente arredondados)
- **Sombras (`box-shadow`):**
  - Padrão (card): `0 4px 16px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.04)`
  - Hover elevado: `0 12px 24px -4px rgba(57, 66, 246, 0.12), 0 4px 8px -2px rgba(0, 0, 0, 0.04)`

---

## 2. Injeção de CSS Base para Streamlit

Sempre que inicializar ou estilizar a aplicação, injete o shell de CSS com `st.markdown(..., unsafe_allow_html=True)`:

```python
import streamlit as st

def inject_design_system():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* Oculta marcas d'água e menus desnecessários do Streamlit */
        header[data-testid="stHeader"], 
        [data-testid="stToolbar"], 
        [data-testid="stDecoration"], 
        [data-testid="stStatusWidget"],
        #MainMenu, footer {
            display: none !important;
        }

        /* Ajuste do container principal */
        .block-container {
            padding-top: 1.8rem !important;
            padding-bottom: 3rem !important;
            max-width: 1300px;
        }

        /* Tipografia global */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Inter', sans-serif;
            color: #0F172A;
        }

        /* Estilização de Botões Nativos */
        .stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            padding: 0.55rem 1.25rem !important;
            transition: all 0.2s ease-in-out !important;
            border: 1px solid transparent !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #3942F6 0%, #2027C9 100%) !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 14px rgba(57, 66, 246, 0.25) !important;
        }

        .stButton > button[kind="primary"]:hover {
            transform: translateY(-1.5px) !important;
            box-shadow: 0 6px 20px rgba(57, 66, 246, 0.35) !important;
        }

        .stButton > button[kind="secondary"] {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #E2E8F0 !important;
        }

        .stButton > button[kind="secondary"]:hover {
            border-color: #CBD5E1 !important;
            background-color: #F8FAFC !important;
            transform: translateY(-1px) !important;
        }

        /* Inputs, Selectbox e Campos de Texto */
        [data-testid="stTextInput"] input, 
        [data-testid="stSelectbox"] > div > div,
        [data-testid="stDateInput"] input {
            border-radius: 8px !important;
            border: 1px solid #E2E8F0 !important;
            background: #FFFFFF !important;
            font-size: 0.9rem !important;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        [data-testid="stTextInput"] input:focus,
        [data-testid="stSelectbox"] > div > div:focus-within {
            border-color: #3942F6 !important;
            box-shadow: 0 0 0 3px rgba(57, 66, 246, 0.15) !important;
        }

        /* Tabs Modernas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #E2E8F0;
            padding: 4px;
            border-radius: 12px;
            border-bottom: none !important;
        }

        .stTabs [data-baseweb="tab"] {
            height: 38px;
            border-radius: 8px;
            font-weight: 500;
            color: #64748B;
            border: none !important;
            background-color: transparent !important;
            padding: 0 16px !important;
            transition: all 0.2s ease;
        }

        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF !important;
            color: #3942F6 !important;
            font-weight: 700 !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
        }

        /* Sidebar Limpa e Elegante */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
```

---

## 3. Componentes Visuais Reutilizáveis

### A. Header / Banner de Boas-Vindas
Substitua headers simples por um banner executivo:

```python
def render_hero_banner(title: str, subtitle: str, badge_text: str = None, user_name: str = None):
    badge_html = f'<div class="badge-pill">{badge_text}</div>' if badge_text else ''
    user_html = f'<div class="user-pill">👤 <b>{user_name}</b></div>' if user_name else ''
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #3942F6 0%, #1E25B6 100%);
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
    ">
        <div>
            <div style="font-size: 1.75rem; font-weight: 800; letter-spacing: -0.5px; margin: 0;">
                {title}
            </div>
            <div style="font-size: 0.95rem; opacity: 0.9; margin-top: 4px;">
                {subtitle}
            </div>
        </div>
        <div style="display: flex; gap: 12px; align-items: center;">
            {badge_html}
            {user_html}
        </div>
    </div>
    """, unsafe_allow_html=True)
```

### B. KPI Cards com Tendência (Métricas Avançadas)
Evite o `st.metric` padrão quando desejar alto impacto visual:

```python
def render_kpi_card(title: str, value: str, delta: str = None, is_positive: bool = True, icon: str = "📊"):
    trend_color = "#10B981" if is_positive else "#EF4444"
    trend_arrow = "↑" if is_positive else "↓"
    delta_html = f'<span style="color: {trend_color}; font-size: 0.82rem; font-weight: 600; margin-left: 8px;">{trend_arrow} {delta}</span>' if delta else ''
    
    st.markdown(f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
        transition: transform 0.2s, box-shadow 0.2s;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 0.85rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;">{title}</span>
            <span style="background: rgba(57, 66, 246, 0.08); padding: 6px 10px; border-radius: 8px; font-size: 1.1rem;">{icon}</span>
        </div>
        <div style="display: flex; align-items: baseline;">
            <span style="font-size: 1.8rem; font-weight: 800; color: #0F172A; letter-spacing: -0.5px;">{value}</span>
            {delta_html}
        </div>
    </div>
    """, unsafe_allow_html=True)
```

### C. Títulos de Seção com Indicador Visual
Crie seções visualmente organizadas com barra de destaque:

```python
def render_section_title(title: str, subtitle: str = None):
    sub_html = f'<div style="font-size: 0.85rem; color: #64748B; margin-top: 2px;">{subtitle}</div>' if subtitle else ''
    st.markdown(f"""
    <div style="margin: 24px 0 16px 0; border-left: 4px solid #3942F6; padding-left: 12px;">
        <div style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin: 0;">{title}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)
```

### D. Badges e Chips de Status
Para listagens, tabelas e cards:

```python
def status_badge(text: str, kind: str = "info") -> str:
    color_map = {
        "success": ("#DEF7EC", "#03543F"),
        "warning": ("#FEF3C7", "#92400E"),
        "danger":  ("#FDE8E8", "#9B1C1C"),
        "info":    ("#E1EFFE", "#1E429F"),
        "brand":   ("rgba(57, 66, 246, 0.12)", "#3942F6"),
    }
    bg, fg = color_map.get(kind, ("#F3F4F6", "#374151"))
    return f"""
    <span style="
        background-color: {bg};
        color: {fg};
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 9999px;
        display: inline-block;
        letter-spacing: 0.3px;
    ">{text}</span>
    """
```

---

## 4. Checklist de Qualidade Visual para Novas Telas

Ao construir ou refatorar qualquer tela:
- [ ] **Hierarquia Clara:** Usar apenas um Hero Banner ou Título H1 no topo.
- [ ] **Alinhamento em Grid:** Utilizar `st.columns([1, 1, 1])` para cartões de métricas em vez de empilhamento vertical.
- [ ] **Contraste & Cores Neutras:** Fundos brancos (`#FFFFFF`) para cartões sobre fundo cinza claro (`#F1F2F4`). Cores fortes apenas para ações e chamadas (`#3942F6`, `#F8B807`).
- [ ] **Inputs Agrupados:** Formulários dentro de containers `with st.container(border=True):` para manter contexto limpo.
- [ ] **Feedback Imediato:** Toasts animados (`st.toast`) para confirmações rápidas e badges contextuais de status.
