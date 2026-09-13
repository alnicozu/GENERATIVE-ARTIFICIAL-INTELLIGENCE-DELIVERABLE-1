import json
import numpy as np
import requests
import warnings
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings("ignore", category=RuntimeWarning)

print("Iniciando Asistente RAG UdeC (Optimizado)...")

print("Cargando cerebro...")
with open('base_conocimiento_udec.json', 'r', encoding='utf-8') as f:
    textos_udec = json.load(f)

# Cargamos el archivo nativo de NumPy
vectores_udec = np.load('vectores_udec.npy')

embedder = SentenceTransformer("intfloat/multilingual-e5-small", device="cpu")

def buscar_mejores_parrafos(pregunta, top_k=5):
    # El modelo E5 exige que le digamos que esto es una "pregunta" (query)
    pregunta_formateada = "query: " + pregunta
    vector_pregunta = embedder.encode([pregunta_formateada], normalize_embeddings=True)
    
    similitudes = cosine_similarity(vector_pregunta, vectores_udec)[0]
    
    indices_ganadores = similitudes.argsort()[-top_k:][::-1]
    
    textos_combinados = ""
    for i, idx in enumerate(indices_ganadores):
        textos_combinados += f"\n[Documento {i+1} - {textos_udec[idx]['fuente']}]: {textos_udec[idx]['texto']}"
        
    return textos_combinados

def preguntar_a_qwen(pregunta, contexto):
    prompt = f"""Eres el asistente oficial de la Universidad de Concepción.
REGLA: Responde basándote ÚNICAMENTE en estos fragmentos del reglamento. Si la respuesta no está, di literalmente: "No está en la normativa".

REGLAMENTOS:
{contexto}

PREGUNTA DEL ALUMNO: {pregunta}
"""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    
    try:
        respuesta = requests.post(url, json=payload)
        return respuesta.json()['response']
    except Exception as e:
        return "Error de conexión con Ollama."

print("\n" + "="*50)
print("¡SISTEMA RAG LISTO! Escribe 'salir' para terminar.")
print("="*50)

while True:
    pregunta = input("\n🧑‍🎓 Tu pregunta: ")
    if pregunta.lower() == 'salir':
        break
        
    print(f"🔍 Buscando en los {len(textos_udec)} fragmentos (NumPy CPU)...")
    textos_contexto = buscar_mejores_parrafos(pregunta, top_k=5)
    
    print(f"📄 Se enviaron los 5 mejores fragmentos al modelo...")
    print("🤖 Qwen está pensando...")
    
    respuesta_ia = preguntar_a_qwen(pregunta, textos_contexto)
    print(f"\n💡 RESPUESTA: {respuesta_ia}")
