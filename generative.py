from langchain_community.llms import Ollama
from langchain import PromptTemplate
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



llm = Ollama(model="llama3", stop=["<|eot_id|>"]) 
template = """
    <|begin_of_text|>
    <|start_header_id|>system<|end_header_id|>
    {system_prompt}
    <|eot_id|>
    <|start_header_id|>user<|end_header_id|>
    {user_prompt}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """
base_prompt = PromptTemplate(
    input_variables=["system_prompt", "user_prompt"],
    template=template
)

system_prompt = """Sei un bullo napoletano sempre arrabbiato di bassa estrazione sociale. Utilizza le frasi di esempio fornite per creare una risposta originale ma breve in napoletano insultando l'entità menzionata nel messaggio dell'utente (usa la traduzione in italiano in parentesi se non sono chiare).
Non devi usare per forza tutte le frasi, scegline solo alcune.
Rivolgiti direttamente all'entità menzionata nel messaggio dell'utente.
NON AGGIUNGERE LE TRADUZIONI IN ITALIANO NELLA RISPOSTA. Rispondi esclusivamente con la risposta in napoletano."""



prompts = {
    "insulto": {
        "system": system_prompt,
        "user": """Frasi di esempio:
```
{examples}
```

L'intento del messaggio dev'essere quello di un saluto all'utente.

Messaggio dell'utente:
```
{message}
```"""
    },

    "saluti": {
        "system": system_prompt,
        "user": """Frasi di esempio:
```
{examples}
```

L'intento del messaggio dev'essere quello di insultare l'entità indicata dall'utente.

Messaggio dell'utente:
```
{message}
```"""
    },
}

# query = "Brother fai i bucchini"



# examples = "\n".join(['Mi scoccio fratello', 'Fratello', 'Fratello', 'Di niente brother'])

# formatted = base_prompt.format(
#     system_prompt=prompts["insulto"]["system"], 
#     user_prompt=prompts["insulto"]["user"].format(examples=examples, message=query)
# )

# print(formatted)