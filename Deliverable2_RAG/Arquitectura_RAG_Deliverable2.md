# Arquitectura RAG — Proyecto GenIA (Deliverable 2)
*Ingeniería Civil Industrial — Universidad de Concepción (Primavera 2026)*  
*Autores: Álvaro Contreras y Pablo Cortés*  
*Repositorio: https://github.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1*

---

## 📌 1. Visión General de la Solución

El objetivo de este entregable es resolver la **Ausencia Paramétrica** identificada en el Entregable 1 (donde el modelo evaluado sin contexto obtuvo un 4.0% de exactitud y alucinó normativas en el 80% de los casos).

Para erradicar la alucinación y dotar al sistema de trazabilidad jurídica estricta, se construyó una arquitectura RAG en 3 niveles:
1. **Ingeniería de Datos y Segmentación por Artículo (*Context-Aware Chunking*)**: 198 fragmentos atómicos etiquetados con su artículo real (`[Art. X°, RI-FI]` y `[Calendario 2026, Semestre]`).
2. **Recuperación Semántica Densa (*Dense Retrieval*)**: Codificación en GPU mediante `intfloat/multilingual-e5-small` (384 dimensiones) y cálculo determinista de similitud coseno con $k=5$ (óptimo de Pareto).
3. **Decodificación Restringida (*Structural Forcing*)**: *System Prompt* con plantilla invariante (`DATO: ... // CITA: ...`) que elimina la divagación y garantiza abstención formal ante premisas falsas.

---

## 🚀 2. Implementación Oficial (Google Colab con GPU NVIDIA Tesla T4)

El pipeline oficial de evaluación académica se encuentra implementado y versionado en el cuaderno:
* **`rag_normativa_ingenieria_4b.ipynb`**:
  * **Hardware Oficial**: GPU NVIDIA Tesla T4 (15.64 GB VRAM).
  * **Modelo Generador**: `Qwen/Qwen3-4B` en precisión `bfloat16` (consumo de **8.53 GB de VRAM**).
  * **Latencia Promedio**: ~0.5 segundos por consulta.
  * **Rendimiento Medido**: **49 / 50 aciertos (98.0%)**, con 100% de precisión en la categoría de abstención (cero alucinaciones).

---

## 💻 3. Implementación Local Complementaria (*Edge AI Portability*)

Como estudio de portabilidad y economía computacional, el repositorio incluye scripts modulares para ejecutar el pipeline de forma 100% offline en procesadores locales (Apple Silicon) mediante Ollama:

1. `paso0_baseline_ollama.py`: Ejecuta la línea base Zero-Shot sin RAG sobre las 50 preguntas.
2. `paso1_extractor_final.py`: ETL y segmentación sintáctica basada en regex con *lookahead* (`(?i)\n(?=art[íi]culo\s+\d+°?)`). Genera `base_conocimiento_udec.json`.
3. `paso2_vectorizador.py`: Vectorización en CPU con `multilingual-e5-small` exportando `vectores_udec.npy`.
4. `paso3_asistente_rag.py`: Modo chat interactivo por consola con forzado de plantilla.
5. `paso4_evaluacion_rag.py`: Harness automatizado para evaluar las 50 preguntas y exportar a CSV.

---

## 📊 4. Trazabilidad de Resultados

* `Deliverable2_RAG/resultados_rag_qwen3_4b.csv`: Salidas oficiales generadas por `Qwen3-4B` en GPU T4.
* `Deliverable2_RAG/reporte_comparativo_50_preguntas.md`: Auditoría forense completa pregunta por pregunta comparando Gold, Baseline y RAG.
* `Deliverable2_RAG/deliverable2.tex`: Documento de 1 página en formato LaTeX con diagrama vectorial TikZ listo para compilar.
