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

# --- CSS PERSONALIZZATO PER MIGLIORARE LA LEGGIBILITÀ ---
st.markdown("""
    <style>
    /* Riduce la dimensione dei font delle metriche (evita l'effetto 'gigante') */
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px !important;
        text-transform: uppercase;
        font-weight: bold;
    }
    /* Rende l'interfaccia più compatta */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Stile per i titoli */
    h1 {
        font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAZIONE GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def carica_dati():
    """Carica i dati direttamente dal foglio Google."""[cite: 3]
    try:
        return conn.read(worksheet="Sheet1", ttl=0) #
    except Exception:
        return pd.DataFrame(columns=['Data Evento', 'Luogo', 'Settore', 'Evento', 'Rischio', 'Keywords']) #

def salva_dati(df):
    """Sovrascrive il foglio Google con il DataFrame aggiornato."""[cite: 3]
    conn.update(worksheet="Sheet1", data=df) #

# Inizializzazione Session State
if 'db_sentinella' not in st.session_state:
    st.session_state.db_sentinella = carica_dati() #

# --- SIDEBAR: PANNELLO OPERATIVO ---
st.sidebar.header("📥 Inserimento Intelligence") #[cite: 3]
with st.sidebar.form("input_form", clear_on_submit=True):
    st.subheader("Analisi Rapida AI") #[cite: 3]
    testo_news = st.text_area("Incolla qui il testo della notizia o del report", height=250) #[cite: 3]
    
    st.sidebar.info("Settori: Energia, Agroalimentare, Cyber, Infrastrutture, Sanità, Economia, Politica") #[cite: 3]
    
    submitted = st.form_submit_button("Analizza e Archivia") #[cite: 3]
    
    if submitted and testo_news:
        with st.spinner("Sentinella sta elaborando e salvando..."): #[cite: 3]
            risultato = analizza_notizia(testo_news) #[cite: 3]
            
            if "error" not in risultato:
                nuova_riga = {
                    'Data Evento': risultato['event_date'],
                    'Luogo': risultato['location'],
                    'Settore': risultato['sector'],
                    'Evento': risultato['summary'],
                    'Rischio': risultato['risk_level'],
                    'Keywords': ", ".join(risultato['keywords'])
                } #[cite: 3]
                
                # Aggiunta in cima
                st.session_state.db_sentinella = pd.concat([
                    pd.DataFrame([nuova_riga]), st.session_state.db_sentinella
                ], ignore_index=True) #[cite: 3]
                
                salva_dati(st.session_state.db_sentinella) #[cite: 3]
                st.toast("Dato archiviato con successo!", icon="✅")
            else:
                st.sidebar.error(f"Errore tecnico: {risultato['error']}") #[cite: 3]

# --- MAIN DASHBOARD: VISUALIZZAZIONE ---
st.title("👁️ Sentinella | Monitoraggio Strategico Italia") #[cite: 3]
st.caption("Database Geopolitico in tempo reale")
st.markdown("---")

# Calcolo metriche dinamiche
if not st.session_state.db_sentinella.empty:
    m1, m2, m3, m4 = st.columns(4) #[cite: 3]
    
    m1.metric("Eventi Archiviati", len(st.session_state.db_sentinella)) #[cite: 3]
    
    try:
        avg_risk = pd.to_numeric(st.session_state.db_sentinella['Rischio']).mean() #[cite: 3]
        m2.metric("Rischio Medio", f"{avg_risk:.1f}/5") #[cite: 3]
    except:
        m2.metric("Rischio Medio", "N/D") #[cite: 3]
    
    top_sector = st.session_state.db_sentinella['Settore'].value_counts().idxmax() #[cite: 3]
    m3.metric("Settore Critico", top_sector) #[cite: 3]
    
    last_loc = st.session_state.db_sentinella.iloc[0]['Luogo'] #[cite: 3]
    m4.metric("Ultimo Focus", last_loc) #[cite: 3]

    st.subheader("📍 Archivio Intelligence Storico")
    
    # --- TABELLA EVOLUTA ---
    # Usiamo data_editor con column_config per gestire le larghezze delle colonne
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
        disabled=True  # Disabilita la modifica manuale per sicurezza
    )

    st.info(f"💡 **Analisi di Sistema:** L'ultimo evento a **{last_loc}** è stato sincronizzato correttamente. Accesso Cloud attivo.") #[cite: 3]
else:
    st.warning("Database cloud vuoto o non connesso. Inserisci una notizia per iniziare.") #[cite: 3]