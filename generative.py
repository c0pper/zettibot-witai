from langchain_community.llms import Ollama
import requests

def is_ollama_available():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        print("Endpoint is reachable. Status code:", response.status_code)
        return True
    except requests.RequestException as e:
        print("Endpoint is not reachable:", e)
        return False




llm = Ollama(model="llama3")

prompts = {
    "insulto": """
### ESEMPI:
{examples}

### ISTRUZIONI:
Sei un bullo napoletano sempre arrabbiato. Utilizza le frasi sopra per creare una risposta originale ma breve in napoletano insultando {entity} (usa la traduzione in italiano in parentesi se non sono chiare).
Non devi usare per forza tutte le frasi, scegline solo alcune.
Rivolgiti direttamente a {entity} nella risposta.
NON AGGIUNGERE LE TRADUZIONI IN ITALIANO NELLA RISPOSTA. Rispondi esclusivamente con la risposta in napoletano.

### MESSAGGIO:
{message}

### RISPOSTA:

"""
}

