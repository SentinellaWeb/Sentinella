import openai
import json
import streamlit as st

# Recupera la chiave in modo sicuro dai Secrets di Streamlit Cloud
# Non scrivere mai la chiave qui dentro!
try:
    api_key_sicura = st.secrets["OPENAI_API_KEY"]
    client = openai.OpenAI(api_key=api_key_sicura)
except Exception:
    # Gestione errore per quando lavori in locale senza secrets
    client = None

def analizza_notizia(testo_grezzo):
    if client is None:
        return {"error": "Configurazione API mancante. Configura i Secrets su Streamlit."}

    settori_ammessi = [
        "Energia", "Agroalimentare", "Cyber-security", 
        "Infrastrutture", "Sanità", "Economia", "Politica"
    ]
    
    prompt = f"""
    Analizza il seguente testo per un servizio di intelligence (Sentinella).
    Restituisci ESCLUSIVAMENTE un oggetto JSON con questi campi:
    - event_date: data dell'evento (YYYY-MM-DD). Se non chiara, usa la data odierna.
    - location: luogo specifico o ambito.
    - geo_scope: una scelta tra [Puntuale, Nazionale, Sovranazionale, Cross-Border].
    - keywords: lista di 3-5 termini chiave.
    - risk_level: intero da 1 a 5.
    - summary: sintesi tecnica di max 200 caratteri.
    - sector: scegli tra {settori_ammessi}.

    Testo: {testo_grezzo}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sei un analista di intelligence geopolitica esperto. Rispondi in JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}