import streamlit as st
import sqlite3
from datetime import date

# Configuração da página para mobile
st.set_page_config(page_title="Tracker 2000kcal", layout="centered")

# Inicialização do banco SQLite
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.set_page_config(page_title="Tracker 2000kcal", layout="centered")

TARGET_KCAL = 2000.0
TARGET_PROT = 170.0
hoje = str(date.today())

# Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    # Carrega dados ignorando cache para refletir novos inserts
    return conn.read(ttl=0)

df = carregar_dados()
if df is None or df.empty:
    df = pd.DataFrame(columns=["data", "alimento", "calorias", "proteinas"])

st.title("Controle Nutricional")

# Formulário de inserção
with st.form("form_registro", clear_on_submit=True):
    alimento = st.text_input("Alimento/Refeição")
    col1, col2 = st.columns(2)
    with col1:
        calorias = st.number_input("Calorias (kcal)", min_value=0.0, step=10.0)
    with col2:
        proteinas = st.number_input("Proteínas (g)", min_value=0.0, step=1.0)
    
    submitted = st.form_submit_button("Registrar")
    if submitted and alimento:
        novo_registro = pd.DataFrame([{
            "data": hoje,
            "alimento": alimento,
            "calorias": calorias,
            "proteinas": proteinas
        }])
        df = pd.concat([df, novo_registro], ignore_index=True)
        conn.update(data=df)
        st.success(f"{alimento} registrado com sucesso!")
        st.rerun()

# Filtragem dos dados de hoje
df["data"] = df["data"].astype(str)
df_hoje = df[df["data"] == hoje]

tot_kcal = float(df_hoje["calorias"].sum()) if not df_hoje.empty else 0.0
tot_prot = float(df_hoje["proteinas"].sum()) if not df_hoje.empty else 0.0

# Métricas
st.subheader(f"Resumo de Hoje ({hoje})")
col_a, col_b = st.columns(2)
col_a.metric("Calorias Restantes", f"{TARGET_KCAL - tot_kcal:.0f} kcal", f"Consumido: {tot_kcal:.0f}")
col_b.metric("Proteínas Restantes", f"{max(0.0, TARGET_PROT - tot_prot):.1f} g", f"Total: {tot_prot:.1f} g")

st.progress(min(1.0, tot_kcal / TARGET_KCAL), text=f"Calorias: {tot_kcal:.0f} / {TARGET_KCAL:.0f} kcal")
st.progress(min(1.0, tot_prot / TARGET_PROT), text=f"Proteína: {tot_prot:.1f} / {TARGET_PROT:.1f} g")

# Histórico
st.subheader("Itens Registrados")
if not df_hoje.empty:
    for _, row in df_hoje.iloc[::-1].iterrows():
        st.write(f"• **{row['alimento']}**: {row['calorias']:.0f} kcal | {row['proteinas']:.1f}g prot")
else:
    st.caption("Nenhum registro para hoje.")

# Parâmetros alvo diários
TARGET_KCAL = 2000.0
TARGET_PROT = 170.0

st.title("Controle Nutricional")
hoje = str(date.today())

# Formulário de inserção rápida
with st.form("form_registro2", clear_on_submit=True):
    alimento = st.text_input("Alimento/Refeição")
    col1, col2 = st.columns(2)
    with col1:
        calorias = st.number_input("Calorias (kcal)", min_value=0.0, step=10.0)
    with col2:
        proteinas = st.number_input("Proteínas (g)", min_value=0.0, step=1.0)
    
    submitted = st.form_submit_button("Registrar")
    if submitted and alimento:
        c.execute("INSERT INTO registros (data, alimento, calorias, proteinas) VALUES (?, ?, ?, ?)",
                  (hoje, alimento, calorias, proteinas))
        conn.commit()

# Consulta dos totais do dia
c.execute("SELECT SUM(calorias), SUM(proteinas) FROM registros WHERE data = ?", (hoje,))
tot_kcal, tot_prot = c.fetchone()
tot_kcal = tot_kcal or 0.0
tot_prot = tot_prot or 0.0

# Métricas de consumo vs teto
st.subheader(f"Resumo de Hoje ({hoje})")
col_a, col_b = st.columns(2)
col_a.metric("Calorias Restantes", f"{TARGET_KCAL - tot_kcal:.0f} kcal", f"Consumido: {tot_kcal:.0f}")
col_b.metric("Proteínas Restantes", f"{max(0.0, TARGET_PROT - tot_prot):.1f} g", f"Total: {tot_prot:.1f} g")

# Barras de progresso
st.progress(min(1.0, tot_kcal / TARGET_KCAL), text=f"Calorias: {tot_kcal:.0f} / {TARGET_KCAL:.0f} kcal")
st.progress(min(1.0, tot_prot / TARGET_PROT), text=f"Proteína: {tot_prot:.1f} / {TARGET_PROT:.1f} g")

# Histórico do dia
st.subheader("Itens Registrados")
c.execute("SELECT alimento, calorias, proteinas FROM registros WHERE data = ? ORDER BY id DESC", (hoje,))
registros = c.fetchall()
for item, kcal, prot in registros:
    st.write(f"• **{item}**: {kcal:.0f} kcal | {prot:.1f}g prot")
