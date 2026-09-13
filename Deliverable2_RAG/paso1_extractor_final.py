import os
import json
import re
import subprocess

print("Iniciando Data Engineering Profesional (Segmentación por Artículo y Calendario Estructurado)...")

ruta_pdfs = '../Corpus/'
if not os.path.exists(ruta_pdfs):
    ruta_pdfs = 'Corpus/'

archivos = [
    'Calendario-Academico-Pregrado-2026.pdf',
    'Reglamento_General_de_Docencia_de_Pregrado.pdf',
    'Reglamento_de_Docencia_de_Pregrado-FI.pdf'
]

def extraer_texto_pdf(ruta_archivo, con_layout=False):
    """Extrae texto con pdftotext si está disponible, o con PyMuPDF (fitz)."""
    cmd = ['/opt/homebrew/bin/pdftotext']
    if con_layout:
        cmd.append('-layout')
    cmd.extend([ruta_archivo, '-'])
    
    try:
        resultado = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
        return resultado
    except Exception:
        pass
        
    try:
        import fitz
        doc = fitz.open(ruta_archivo)
        texto = ""
        for p in doc:
            texto += p.get_text() + "\n"
        return texto
    except Exception as e:
        print(f"Error al leer {ruta_archivo}: {e}")
        return ""

def procesar_calendario(texto_layout):
    """Extrae eventos del calendario vinculando en un solo chunk el evento con su fecha y semestre."""
    chunks = []
    semestre = "Año Académico 2026"
    
    for linea in texto_layout.split('\n'):
        linea = linea.strip()
        if not linea:
            continue
            
        if "PRIMER SEMESTRE" in linea.upper():
            semestre = "Primer Semestre 2026"
            continue
        elif "SEGUNDO SEMESTRE" in linea.upper():
            semestre = "Segundo Semestre 2026"
            continue
            
        # Buscar fechas en la línea
        match_fecha = re.search(r'(\d{1,2}.*?(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(?:\s+de\s+\d{4})?)', linea, re.IGNORECASE)
        if match_fecha:
            fecha = match_fecha.group(1).strip()
            evento = linea[:match_fecha.start()].strip()
            evento = re.sub(r'\s{2,}', ' ', evento)
            evento = evento.rstrip(':–- ')
            
            # Filtro de ruido
            if len(evento) >= 3 and "fono" not in evento.lower() and "calle" not in evento.lower():
                chunks.append(f"[Calendario 2026, {semestre}]: {evento} — {fecha}")
                
    return chunks

def procesar_reglamento(texto_raw, nombre_archivo):
    """Segmenta el reglamento por cada Artículo individualmente, conservando citas y contexto."""
    abrev = "RG" if "General" in nombre_archivo else "RI-FI"
    
    # 1. Unir palabras cortadas por guion al final de linea
    texto = re.sub(r'(\w+)-\n(\w+)', r'\1\2', texto_raw)
    
    # 2. Dividir estrictamente por el inicio de cada Artículo
    bloques_articulos = re.split(r'(?i)\n(?=art[íi]culo\s+\d+°?|art\.\s*\d+°?)', texto)
    
    chunks = []
    
    for bloque in bloques_articulos:
        bloque = bloque.strip()
        if not bloque:
            continue
            
        # Detectar el número de artículo del bloque
        match_art = re.search(r'(?i)(art[íi]culo\s+\d+°?|art\.\s*\d+°?)', bloque)
        if match_art:
            num_match = re.search(r'\d+°?', match_art.group(0))
            articulo_tag = f"Art. {num_match.group(0)}" if num_match else "Artículo"
        else:
            articulo_tag = "Disposiciones Generales"
            
        prefijo = f"[{articulo_tag}, {abrev}]: "
        
        # Limpiar saltos de línea internos convirtiéndolos en espacios limpios
        texto_limpio = re.sub(r'\s*\n\s*', ' ', bloque)
        texto_limpio = re.sub(r'\s{2,}', ' ', texto_limpio)
        
        if len(texto_limpio) < 30:
            continue
            
        # Si el artículo es breve (<= 800 caracteres), se guarda entero en un solo chunk
        if len(texto_limpio) <= 800:
            chunks.append(f"{prefijo}{texto_limpio}")
        else:
            # Si el artículo es largo, se divide por oraciones garantizando que cada sub-chunk conserve la cita
            oraciones = texto_limpio.split('. ')
            chunk_actual = ""
            
            for oracion in oraciones:
                oracion_con_punto = oracion.strip() + ". "
                if len(chunk_actual) + len(oracion_con_punto) > 750:
                    if chunk_actual:
                        chunks.append(f"{prefijo}{chunk_actual.strip()}")
                    chunk_actual = oracion_con_punto
                else:
                    chunk_actual += oracion_con_punto
                    
            if chunk_actual:
                chunks.append(f"{prefijo}{chunk_actual.strip()}")
                
    return chunks

chunks_totales = []

for archivo in archivos:
    ruta_completa = os.path.join(ruta_pdfs, archivo)
    if not os.path.exists(ruta_completa):
        print(f"ADVERTENCIA: No se encontró {ruta_completa}")
        continue
        
    print(f"Procesando: {archivo}...")
    
    if "Calendario" in archivo:
        texto = extraer_texto_pdf(ruta_completa, con_layout=True)
        chunks_archivo = procesar_calendario(texto)
    else:
        texto = extraer_texto_pdf(ruta_completa, con_layout=False)
        chunks_archivo = procesar_reglamento(texto, archivo)
        
    print(f" -> {len(chunks_archivo)} fragmentos semánticos extraídos.")
    
    for c in chunks_archivo:
        chunks_totales.append({"fuente": archivo, "texto": c})

print(f"\n✅ Base de conocimiento reconstruida con éxito: {len(chunks_totales)} chunks totales.")

salida_json = 'base_conocimiento_udec.json'
with open(salida_json, 'w', encoding='utf-8') as f:
    json.dump(chunks_totales, f, ensure_ascii=False, indent=4)

print(f"Archivo guardado en {salida_json}")
