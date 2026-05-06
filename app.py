import streamlit as st
import pandas as pd
from datetime import datetime
from processor import analizza_notizia
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Sentinella | Intelligence Strategica", 
    layout="wide", 
    page_icon="👁️"
)

# --- CSS PERSONALIZZATO ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 24px !important; }
    [data-testid="stMetricLabel"] { font-size: 14px !important; text-transform: uppercase; font-weight: bold; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAZIONE GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Recuperiamo l'ID dello spreadsheet dai secrets
SPREADSHEET_ID = st.secrets["connections"]["gsheets"]["spreadsheet"]

def carica_dati():
    """Carica i dati usando esplicitamente l'ID dello spreadsheet."""
    try:
        return conn.read(spreadsheet=SPREADSHEET_ID, worksheet="Sheet1", ttl=0) 
    except Exception:
        return pd.DataFrame(columns=['Data Evento', 'Luogo', 'Settore', 'Evento', 'Rischio', 'Keywords'])

def salva_dati(df):
    """Aggiorna il foglio Google usando l'ID univoco."""
    conn.update(spreadsheet=SPREADSHEET_ID, worksheet="Sheet1", data=df) 

# Inizializzazione Session State
if 'db_sentinella' not in st.session_state:
    st.session_state.db_sentinella = carica_dati()

# --- SIDEBAR: PANNELLO OPERATIVO ---
st.sidebar.header("📥 Inserimento Intelligence")
with st.sidebar.form("input_form", clear_on_submit=True):
    st.subheader("Analisi Rapida AI")
    testo_news = st.text_area("Incolla qui il testo della notizia o del report", height=250)
    
    st.sidebar.info("Settori monitorati: Energia, Agroalimentare, Cyber, Infrastrutture, Sanità, Economia, Politica")
    
    submitted = st.form_submit_button("Analizza e Archivia")
    
    if submitted and testo_news:
        with st.spinner("Sentinella sta elaborando e salvando..."):
            risultato = analizza_notizia(testo_news)
            
            if "error" not in risultato:
                nuova_riga = {
                    'Data Evento': risultato['event_date'],
                    'Luogo': risultato['location'],
                    'Settore': risultato['sector'],
                    'Evento': risultato['summary'],
                    'Rischio': risultato['risk_level'],
                    'Keywords': ", ".join(risultato['keywords'])
                }
                
                st.session_state.db_sentinella = pd.concat([
                    pd.DataFrame([nuova_riga]), st.session_state.db_sentinella
                ], ignore_index=True)
                
                salva_dati(st.session_state.db_sentinella)
                st.toast("Dato archiviato con successo!", icon="✅")
            else:
                st.sidebar.error(f"Errore tecnico: {risultato['error']}")

# --- MAIN DASHBOARD: VISUALIZZAZIONE ---
st.title("👁️ Sentinella | Monitoraggio Strategico Italia")
st.caption("Database Geopolitico in tempo reale sincronizzato su Cloud")
st.markdown("---")

if not st.session_state.db_sentinella.empty:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Eventi Archiviati", len(st.session_state.db_sentinella))
    
    try:
        avg_risk = pd.to_numeric(st.session_state.db_sentinella['Rischio']).mean()
        m2.metric("Rischio Medio", f"{avg_risk:.1f}/5")
    except:
        m2.metric("Rischio Medio", "N/D")
    
    top_sector = st.session_state.db_sentinella['Settore'].value_counts().idxmax()
    m3.metric("Settore Critico", top_sector)
    
    last_loc = st.session_state.db_sentinella.iloc[0]['Luogo']
    m4.metric("Ultimo Focus", last_loc)

    st.subheader("📍 Archivio Intelligence Storico")
    st.data_editor(
        st.session_state.db_sentinella,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Data Evento": st.column_config.TextColumn("Data", width="small"),
            "Luogo": st.column_config.TextColumn("Luogo", width="small"),
            "Settore": st.column_config.TextColumn("Settore", width="small"),
            "Evento": st.column_config.TextColumn("Descrizione Analitica", width="large"),
            "Rischio": st.column_config.NumberColumn("Rischio", format="%d ⭐", width="small"),
            "Keywords": st.column_config.TextColumn("Keywords", width="medium"),
        },
        disabled=True
    )
else:
    st.warning("Database cloud vuoto o non connesso. Inserisci una notizia nella sidebar per iniziare.")