import streamlit as st
import pandas as pd
from datetime import date

# Configuração da página
st.set_page_config(page_title="Gestão de Refeitório", layout="wide")

st.title("🍽️ Registro de Almoço - Escala 12 Dias")

# Carregar base de dados
@st.cache_data
def load_data():
    return pd.read_csv('base_inscritos.csv')

if 'df' not in st.session_state:
    st.session_state.df = load_data()

if 'presencas' not in st.session_state:
    st.session_state.presencas = pd.DataFrame(columns=['Data', 'Nome', 'CPF', 'Email'])

# --- BUSCA E REGISTRO ---
st.header("1. Registrar Presença")
busca = st.text_input("Busque por Nome ou E-mail")

if busca:
    # Filtro simples (Fuzzy search básica)
    resultados = st.session_state.df[
        st.session_state.df['Nome'].str.contains(busca, case=False) | 
        st.session_state.df['Email'].str.contains(busca, case=False)
    ]
    
    if not resultados.empty:
        for idx, row in resultados.iterrows():
            with st.expander(f"Confirmar: {row['Nome']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**E-mail:** {row['Email']}")
                    st.write(f"**Telefone:** {row['Telefone']}")
                
                with col2:
                    # Se o CPF estiver vazio, pede para preencher
                    cpf_atual = row['CPF'] if pd.notnull(row['CPF']) and row['CPF'] != '' else ""
                    novo_cpf = st.text_input(f"Confirme/Insira o CPF para {row['Nome']}", value=cpf_atual, key=f"cpf_{idx}")
                    
                if st.button(f"Confirmar Almoço para Hoje", key=f"btn_{idx}"):
                    # Atualizar CPF na base se foi preenchido agora
                    st.session_state.df.at[idx, 'CPF'] = novo_cpf
                    
                    # Registrar presença
                    nova_presenca = pd.DataFrame([{
                        'Data': date.today(),
                        'Nome': row['Nome'],
                        'CPF': novo_cpf,
                        'Email': row['Email']
                    }])
                    st.session_state.presencas = pd.concat([st.session_state.presencas, nova_presenca], ignore_index=True)
                    st.success(f"✅ Almoço registrado para {row['Nome']}!")

# --- DASHBOARD ---
st.divider()
st.header("2. Resumo do Dia")
hoje = date.today()
total_hoje = len(st.session_state.presencas[st.session_state.presencas['Data'] == hoje])

c1, c2 = st.columns(2)
c1.metric("Senhas Necessárias Hoje", total_hoje)
c2.write("Lista de Confirmados:")
c2.dataframe(st.session_state.presencas[st.session_state.presencas['Data'] == hoje][['Nome', 'CPF']])

# --- EXPORTAÇÃO ---
st.sidebar.header("Administração")
if st.sidebar.button("Baixar Lista de Presenças (CSV)"):
    csv = st.session_state.presencas.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("Clique aqui para baixar", csv, "presencas.csv", "text/csv")

if st.sidebar.button("Baixar Base Atualizada (com novos CPFs)"):
    csv_base = st.session_state.df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("Baixar Base_Inscritos_v2.csv", csv_base, "base_inscritos_v2.csv", "text/csv")
