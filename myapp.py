import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- Funções de Banco de Dados SQLite ---
def init_db():
    conn = sqlite3.connect("logs.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            data TEXT PRIMARY KEY,
            contagem INTEGER
        )
    """)
    conn.commit()
    return conn

conn = init_db()

def get_today_count(today):
    cursor = conn.cursor()
    cursor.execute("SELECT contagem FROM logs WHERE data = ?", (today,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        # Cria o registro para hoje se não existir
        cursor.execute("INSERT INTO logs (data, contagem) VALUES (?, ?)", (today, 0))
        conn.commit()
        return 0

def update_today_count(today, count):
    cursor = conn.cursor()
    cursor.execute("UPDATE logs SET contagem = ? WHERE data = ?", (count, today))
    conn.commit()

def get_all_logs():
    query = "SELECT data, contagem FROM logs"
    df = pd.read_sql(query, conn)
    return df

# --- Lógica do Dashboard ---
today = datetime.today().strftime("%d-%m-%Y")
current_count = get_today_count(today)
if "current_count" not in st.session_state:
    st.session_state.current_count = current_count

st.title("Dashboard de Progresso (Mestres Convertidos)")
st.metric(label="Contagem atual de mestres convertidos", value=f"{st.session_state.current_count}/465")

col1, col2 = st.columns(2)
with col1:
    if st.button("Adicionar Mestre"):
        st.session_state.current_count += 1
        update_today_count(today, st.session_state.current_count)
        st.success("Mestre adicionado! Atualize a página para ver a mudança.")
with col2:
    if st.button("Remover Mestre"):
        if st.session_state.current_count > 0:
            st.session_state.current_count -= 1
            update_today_count(today, st.session_state.current_count)
            st.success("Mestre removido! Atualize a página para ver a mudança.")
        else:
            st.warning("A contagem já está em 0!")

st.write(f"Contagem atual para {today}: {st.session_state.current_count}")

tabs = st.tabs(["Histórico", "Evolução"])

with tabs[0]:
    st.subheader("Histórico de Contagens")
    df_log = get_all_logs()
    df_log_ordenado = df_log.sort_values("data")
    data_selecionada = st.selectbox("Escolha uma data", df_log_ordenado["data"].unique())
    df_filtrado = df_log_ordenado[df_log_ordenado["data"] == data_selecionada]
    st.dataframe(df_filtrado.reset_index(drop=True))

with tabs[1]:
    st.subheader("Evolução da Contagem")
    df_log = get_all_logs()
    chart_data = df_log.copy()
    # Converte a coluna 'data' para datetime para ordenação e plotagem
    chart_data["data"] = pd.to_datetime(chart_data["data"], format="%d-%m-%Y")
    chart_data = chart_data.sort_values("data").set_index("data")
    st.line_chart(chart_data["contagem"])

if __name__ == "__main__":
    main()
