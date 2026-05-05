import streamlit as st
import pandas as pd
import os
from datetime import datetime
from processor import analizza_notizia

# --- CONFIGURAZIONE PERSISTENZA ---
# Il file verrà salvato nella stessa cartella dello script sul tuo hosting
DB_FILE = "database_sentinella.csv"

def carica_dati():
    """Carica i dati dal file CSV se esiste, altrimenti crea un DataFrame vuoto."""
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except Exception:
            return pd.DataFrame(columns=['Data Evento', 'Luogo', 'Settore', 'Evento', 'Rischio', 'Keywords'])
    else:
        return pd.DataFrame(columns=['Data Evento', 'Luogo', 'Settore', 'Evento', 'Rischio', 'Keywords'])

def salva_dati(df):
    """Salva il DataFrame su file CSV fisicamente sul server."""
    df.to_csv(DB_FILE, index=False)

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Sentinella | Intelligence Strategica", layout="wide")

# Inizializzazione Session State con i dati salvati su disco
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
        with st.spinner("Sentinella sta elaborando e salvando i dati..."):
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
                
                # SALVATAGGIO FISICO: Scrive il file sul tuo spazio hosting
                salva_dati(st.session_state.db_sentinella)
                
                st.sidebar.success("Dato analizzato e salvato permanentemente!")
            else:
                st.sidebar.error(f"Errore tecnico: {risultato['error']}")

# --- MAIN DASHBOARD: VISUALIZZAZIONE ---
st.title("👁️ Sentinella | Monitoraggio Strategica Italia")
st.markdown("---")

# Calcolo metriche dinamiche in tempo reale
if not st.session_state.db_sentinella.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    # Conteggio eventi
    col1.metric("Eventi Archiviati", len(st.session_state.db_sentinella))
    
    # Rischio Medio (calcolato sul totale storico)
    try:
        avg_risk = pd.to_numeric(st.session_state.db_sentinella['Rischio']).mean()
        col2.metric("Rischio Medio", f"{avg_risk:.1f}/5")
    except:
        col2.metric("Rischio Medio", "N/D")
    
    # Settore più frequente
    top_sector = st.session_state.db_sentinella['Settore'].value_counts().idxmax()
    col3.metric("Settore Critico", top_sector)
    
    # Ultimo focus geografico
    last_loc = st.session_state.db_sentinella.iloc[0]['Luogo']
    col4.metric("Ultimo Focus", last_loc)

    st.subheader("📍 Database Intelligence Storico")
    # Tabella interattiva
    st.dataframe(st.session_state.db_sentinella, use_container_width=True)

    # Box Analisi Predittiva (Logica AI simulata basata sull'ultimo inserimento)
    st.info(f"💡 **Analisi di Sistema:** L'ultimo evento registrato a **{last_loc}** (Settore: {top_sector}) "
            f"è stato classificato con rischio {st.session_state.db_sentinella.iloc[0]['Rischio']}. "
            "Monitorare possibili reazioni a catena nei nodi logistici adiacenti.")
else:
    st.warning("Il database è vuoto. Inserisci una notizia nella sidebar per iniziare il monitoraggio.")