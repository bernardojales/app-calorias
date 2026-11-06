import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.set_page_config(page_title="Tracker 2000kcal", layout="centered")

TARGET_KCAL = 2000.0
TARGET_PROT = 170.0
hoje = str(date.today())

st.title("Controle Nutricional")

conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        dados = conn.read(ttl=0)
        if dados is not None and not dados.empty:
            return dados
    except Exception:
        pass
    return pd.DataFrame(columns=["data", "alimento", "calorias", "proteinas"])

df = carregar_dados()

with st.form("form_registro_principal", clear_on_submit=True):
    alimento = st.text_input("Alimento/Refeição")
    col1, col2 = st.columns(2)
    with col1:
        calorias = st.number_input("Calorias (kcal)", min_value=0.0, step=10.0)
    with col2:
        proteinas = st.number_input("Proteínas (g)", min_value=0.0, step=1.0)
    
    submitted = st.form_submit_button("Registrar")
    if submitted and alimento:
        novo = pd.DataFrame([{
            "data": hoje,
            "alimento": alimento,
            "calorias": calorias,
            "proteinas": proteinas
        }])
        df = pd.concat([df, novo], ignore_index=True)
        conn.update(data=df)
        st.success(f"{alimento} registrado!")
        st.rerun()

df["data"] = df["data"].astype(str)
df_hoje = df[df["data"] == hoje]

tot_kcal = float(df_hoje["calorias"].sum()) if not df_hoje.empty else 0.0
tot_prot = float(df_hoje["proteinas"].sum()) if not df_hoje.empty else 0.0

st.subheader(f"Resumo de Hoje ({hoje})")
col_a, col_b = st.columns(2)
col_a.metric("Calorias Restantes", f"{TARGET_KCAL - tot_kcal:.0f} kcal", f"Consumido: {tot_kcal:.0f}")
col_b.metric("Proteínas Restantes", f"{max(0.0, TARGET_PROT - tot_prot):.1f} g", f"Total: {tot_prot:.1f} g")

st.progress(min(1.0, tot_kcal / TARGET_KCAL), text=f"Calorias: {tot_kcal:.0f} / {TARGET_KCAL:.0f} kcal")
st.progress(min(1.0, tot_prot / TARGET_PROT), text=f"Proteína: {tot_prot:.1f} / {TARGET_PROT:.1f} g")

st.subheader("Itens Registrados")
if not df_hoje.empty:
    for _, row in df_hoje.iloc[::-1].iterrows():
        st.write(f"• **{row['alimento']}**: {row['calorias']:.0f} kcal | {row['proteinas']:.1f}g prot")
else:
    st.caption("Nenhum registro para hoje.")
