import csv
import requests
import json
import time

print("Iniciando Evaluación Baseline (Ollama local - qwen2.5:3b)...")

SYSTEM = (
    "Eres un asistente experto en la normativa de pregrado de la Facultad de "
    "Ingeniería de la Universidad de Concepción. Responde de forma breve, con el "
    "dato exacto y citando el artículo correspondiente (por ejemplo: 'Art. 8'). "
    "Si no tienes la información, di explícitamente que no está en la normativa."
)

def preguntar_a_ollama(pregunta):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "qwen2.5:3b",
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": pregunta}
        ],
        "stream": False,
        "options": {"temperature": 0.0} # Equivalente a do_sample=False
    }
    
    try:
        respuesta = requests.post(url, json=payload)
        return respuesta.json()['message']['content'].strip()
    except Exception as e:
        return f"ERROR_OLLAMA: {str(e)}"

# Cargar dataset
input_file = '../test_set_50.csv'
output_file = 'resultados_baseline_qwen2.5.csv'

resultados = []
with open(input_file, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    filas = list(reader)
    total = len(filas)
    
    print(f"Evaluando {total} preguntas sin RAG...")
    for i, fila in enumerate(filas):
        print(f"[{i+1}/{total}] Pregunta: {fila['pregunta']}")
        respuesta = preguntar_a_ollama(fila['pregunta'])
        
        # Copiar todos los campos originales y añadir la respuesta
        fila_resultado = fila.copy()
        fila_resultado['prediccion_baseline'] = respuesta
        resultados.append(fila_resultado)
        
        time.sleep(0.1) # Pequeña pausa para no saturar

# Guardar resultados
if resultados:
    fieldnames = list(resultados[0].keys())
    with open(output_file, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resultados)
        
print(f"✅ Evaluación Baseline completada. Guardado en {output_file}")
