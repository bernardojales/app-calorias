import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import text

st.set_page_config(page_title="Tracker 2000kcal", layout="centered")

TARGET_KCAL = 2000.0
TARGET_PROT = 170.0
hoje = str(date.today())

st.title("Controle Nutricional")

# Conexão relacional usando a URL do Supabase salva nos secrets
conn = st.connection("sql", url=st.secrets["SUPABASE_URL"])

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
        with conn.session as s:
            s.execute(
                text("INSERT INTO registros (data, alimento, calorias, proteinas) VALUES (:d, :a, :c, :p)"),
                {"d": hoje, "a": alimento, "c": calorias, "p": proteinas}
            )
            s.commit()
        st.success(f"{alimento} registrado com sucesso!")
        st.rerun()

# Leitura dos registros da data atual (ttl=0 garante leitura sem cache local)
df_hoje = conn.query(
    "SELECT id, alimento, calorias, proteinas FROM registros WHERE data = :d ORDER BY id DESC",
    params={"d": hoje},
    ttl=0
)

tot_kcal = float(df_hoje["calorias"].sum()) if not df_hoje.empty else 0.0
tot_prot = float(df_hoje["proteinas"].sum()) if not df_hoje.empty else 0.0

# Painel de métricas
st.subheader(f"Resumo de Hoje ({hoje})")
col_a, col_b = st.columns(2)
col_a.metric("Calorias Restantes", f"{TARGET_KCAL - tot_kcal:.0f} kcal", f"Consumido: {tot_kcal:.0f}")
col_b.metric("Proteínas Restantes", f"{max(0.0, TARGET_PROT - tot_prot):.1f} g", f"Total: {tot_prot:.1f} g")

st.progress(min(1.0, tot_kcal / TARGET_KCAL), text=f"Calorias: {tot_kcal:.0f} / {TARGET_KCAL:.0f} kcal")
st.progress(min(1.0, tot_prot / TARGET_PROT), text=f"Proteína: {tot_prot:.1f} / {TARGET_PROT:.1f} g")

# Listagem dos itens
st.subheader("Itens Registrados")
if not df_hoje.empty:
    for _, row in df_hoje.iterrows():
        st.write(f"• **{row['alimento']}**: {row['calorias']:.0f} kcal | {row['proteinas']:.1f}g prot")
else:
    st.caption("Nenhum registro para hoje.")
