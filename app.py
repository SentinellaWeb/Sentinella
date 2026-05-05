import streamlit as st
import pandas as pd
from datetime import datetime
from processor import analizza_notizia
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAZIONE GOOGLE SHEETS ---
# Sostituiamo il file locale CSV con la connessione cloud
conn = st.connection("gsheets", type=GSheetsConnection)

def carica_dati():
    """Carica i dati direttamente dal foglio Google."""
    try:
        # Legge il foglio principale (Sheet1)
        return conn.read(worksheet="Sheet1", ttl=0) # ttl=0 forza l'aggiornamento dati
    except Exception:
        # Se il foglio è vuoto o non raggiungibile, restituisce la struttura base
        return pd.DataFrame(columns=['Data Evento', 'Luogo', 'Settore', 'Evento', 'Rischio', 'Keywords'])

def salva_dati(df):
    """Sovrascrive il foglio Google con il DataFrame aggiornato."""
    conn.update(worksheet="Sheet1", data=df)

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Sentinella | Intelligence Strategica", layout="wide")

# Inizializzazione Session State con i dati da Google Sheets
if 'db_sentinella' not in st.session_state:
    st.session_state.db_sentinella = carica_dati()

# --- SIDEBAR: PANNELLO OPERATIVO ---
st.sidebar.header("📥 Inserimento Intelligence")
with st.sidebar.form("input_form"):
    st.subheader("Analisi Rapida AI")
    testo_news = st.text_area("Incolla qui il testo della notizia o del report", height=250)
    
    st.sidebar.info("Settori monitorati: Energia, Agroalimentare, Cyber, Infrastrutture, Sanità, Economia, Politica")
    
    submitted = st.form_submit_button("Analizza e Archivia")
    
    if submitted and testo_news:
        with st.spinner("Sentinella sta scrivendo su Google Sheets..."):
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
                
                # Aggiunta in cima al DataFrame in memoria
                st.session_state.db_sentinella = pd.concat([
                    pd.DataFrame([nuova_riga]), st.session_state.db_sentinella
                ], ignore_index=True)
                
                # SALVATAGGIO CLOUD: Scrive direttamente sul foglio Google
                salva_dati(st.session_state.db_sentinella)
                
                st.sidebar.success("Dato archiviato su Google Sheets!")
            else:
                st.sidebar.error(f"Errore tecnico: {risultato['error']}")

# --- MAIN DASHBOARD: VISUALIZZAZIONE ---
st.title("👁️ Sentinella | Monitoraggio Strategico Italia")
st.markdown("---")

# Calcolo metriche dinamiche in tempo reale
if not st.session_state.db_sentinella.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Eventi Archiviati", len(st.session_state.db_sentinella))
    
    try:
        avg_risk = pd.to_numeric(st.session_state.db_sentinella['Rischio']).mean()
        col2.metric("Rischio Medio", f"{avg_risk:.1f}/5")
    except:
        col2.metric("Rischio Medio", "N/D")
    
    top_sector = st.session_state.db_sentinella['Settore'].value_counts().idxmax()
    col3.metric("Settore Critico", top_sector)
    
    last_loc = st.session_state.db_sentinella.iloc[0]['Luogo']
    col4.metric("Ultimo Focus", last_loc)

    st.subheader("📍 Database Intelligence Storico (Cloud)")
    st.dataframe(st.session_state.db_sentinella, use_container_width=True)

    st.info(f"💡 **Analisi di Sistema:** L'ultimo evento a **{last_loc}** richiede attenzione costante. "
            "I dati sono sincronizzati in tempo reale con il database centrale.")
else:
    st.warning("Database cloud vuoto o non connesso. Inserisci una notizia per inizializzare.")