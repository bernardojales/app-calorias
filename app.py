import streamlit as st
from datetime import date
from supabase import create_client, Client

st.set_page_config(page_title="Tracker 2000kcal", layout="centered")

# Validação explícita para garantir que os Secrets corretos foram carregados
if "SUPABASE_URL" not in st.secrets or "SUPABASE_KEY" not in st.secrets:
    st.error("Configure SUPABASE_URL e SUPABASE_KEY nos Secrets do Streamlit.")
    st.stop()

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]

if url.startswith("postgresql"):
    st.error("A variável SUPABASE_URL ainda está com a string 'postgresql://'. Troque pela URL 'https://...' da aba API do Supabase.")
    st.stop()

# Inicializa o cliente via HTTPS (API REST)
supabase: Client = create_client(url, key)

TARGET_KCAL = 2000.0
TARGET_PROT = 170.0
hoje = str(date.today())

st.title("Controle Nutricional")

# Formulário de inserção
with st.form("form_registro_principal", clear_on_submit=True):
    alimento = st.text_input("Alimento/Refeição")
    col1, col2 = st.columns(2)
    with col1:
        calorias = st.number_input("Calorias (kcal)", min_value=0.0, step=10.0)
    with col2:
        proteinas = st.number_input("Proteínas (g)", min_value=0.0, step=1.0)
    
    submitted = st.form_submit_button("Registrar")
    if submitted and alimento:
        supabase.table("registros").insert({
            "data": hoje,
            "alimento": alimento,
            "calorias": float(calorias),
            "proteinas": float(proteinas)
        }).execute()
        st.success(f"{alimento} registrado com sucesso!")
        st.rerun()

# Busca os dados do dia via HTTPS
response = (
    supabase.table("registros")
    .select("id, alimento, calorias, proteinas")
    .eq("data", hoje)
    .order("id", desc=True)
    .execute()
)

registros = response.data or []

tot_kcal = sum(float(r["calorias"]) for r in registros)
tot_prot = sum(float(r["proteinas"]) for r in registros)

# Painel de métricas
st.subheader(f"Resumo de Hoje ({hoje})")
col_a, col_b = st.columns(2)
col_a.metric("Calorias Restantes", f"{TARGET_KCAL - tot_kcal:.0f} kcal", f"Consumido: {tot_kcal:.0f}")
col_b.metric("Proteínas Restantes", f"{max(0.0, TARGET_PROT - tot_prot):.1f} g", f"Total: {tot_prot:.1f} g")

st.progress(min(1.0, tot_kcal / TARGET_KCAL), text=f"Calorias: {tot_kcal:.0f} / {TARGET_KCAL:.0f} kcal")
st.progress(min(1.0, tot_prot / TARGET_PROT), text=f"Proteína: {tot_prot:.1f} / {TARGET_PROT:.1f} g")

# Listagem de itens
st.subheader("Itens Registrados")
if registros:
    for r in registros:
        st.write(f"• **{r['alimento']}**: {r['calorias']:.0f} kcal | {r['proteinas']:.1f}g prot")
else:
    st.caption("Nenhum registro para hoje.")
