import streamlit as st

st.set_page_config(
    page_title="Smart Vision — Gestão de Estoque Óptico",
    page_icon="👓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("👓 Smart Vision")
st.subheader("Sistema de Gerenciamento de Estoque para Óticas")

st.success("✅ Ambiente Streamlit configurado e operacional com sucesso!")

with st.expander("ℹ️ Informações do Ambiente e Status", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Frontend", value="Streamlit v1.65.0")
    with col2:
        st.metric(label="Backend", value="Python + Xano")
    with col3:
        st.metric(label="Banco de Dados", value="SQL Server / T-SQL")

st.markdown("""
### 📋 Próximos Passos do Desenvolvimento:
1. **Modelagem & Domínio**: Consultar `docs/domain-model.md` e `docs/project-overview.md`.
2. **OpenSpec Workflows**: Executar ciclo de mudanças incrementais (`Explore` ➔ `Propose` ➔ `Review` ➔ `Apply` ➔ `Archive`).
3. **Sincronização Xano**: Utilizar `xano workspace pull` e `xano workspace push -d ./xano --dry-run`.
4. **Regras Operacionais**: Seguir diretrizes de auditoria e permissões em `AGENTS.md`.
""")
