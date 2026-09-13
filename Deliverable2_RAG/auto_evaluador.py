import csv
import re
import unicodedata

def normalize(text):
    if not text: return ""
    text = str(text).lower()
    # Quitar tildes
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    # Quitar todo menos alfanumericos
    text = re.sub(r'[^a-z0-9]', '', text)
    return text

with open('resultados_rag_qwen2.5.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

correctos = []
solo_cita = []
solo_dato = []
abstencion = []
errores = []

for idx, r in enumerate(rows):
    pred = normalize(r['prediccion_rag'])
    pred_raw = r['prediccion_rag']
    dato = normalize(r['gold_dato'])
    fuente = r['gold_fuente']
    
    # Extraer el número de artículo de la fuente gold
    num_match = re.search(r'\d+', fuente)
    fuente_num = num_match.group(0) if num_match else "NONE"
    
    if "normativa" in pred and "no" in pred and len(pred) < 30:
        abstencion.append(idx+1)
        continue
        
    # Lógica de match relajada
    has_dato = dato in pred
    # Truco para "4,0" vs "4.0" vs "4"
    if not has_dato and "4" in dato:
        if "40" in pred or "4,0" in pred_raw or "4.0" in pred_raw or "cuatro" in pred:
            has_dato = True
            
    has_cita = fuente_num in pred
    if not has_cita:
        # Check string raw just in case
        if fuente_num in pred_raw:
            has_cita = True
            
    if has_dato and has_cita:
        correctos.append(idx+1)
    elif has_cita and not has_dato:
        solo_cita.append(idx+1)
    elif has_dato and not has_cita:
        solo_dato.append(idx+1)
    else:
        errores.append(idx+1)

print(f"✅ Correctos Completos (Dato + Cita): {len(correctos)}")
print(f"⚠️ Incompletos (Solo Cita): {len(solo_cita)}")
print(f"⚠️ Incompletos (Solo Dato): {len(solo_dato)}")
print(f"🤷‍♂️ Abstenciones: {len(abstencion)}")
print(f"❌ Errores/Alucinaciones: {len(errores)}")

print("\n--- DETALLE DE LOS INCOMPLETOS (Solo Cita) ---")
for i in solo_cita[:3]:
    print(f"P{i}: {rows[i-1]['prediccion_rag']} (Le faltó mencionar el dato: {rows[i-1]['gold_dato']})")
    
print("\n--- DETALLE DE ERRORES ---")
for i in errores[:3]:
    print(f"P{i}: {rows[i-1]['prediccion_rag'][:100]}...")
