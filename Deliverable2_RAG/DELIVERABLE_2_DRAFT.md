# Borrador Técnico Final — Deliverable 2 (LaTeX 1-Página)
*Proyecto Semestral: Inteligencia Artificial Generativa (580694) — Primavera 2026*  
*Equipo: Álvaro Contreras y Pablo Cortés*  
*Repositorio Oficial: https://github.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1*  

---

### 1. Model Commitment & Hardware Declaration
El equipo ratifica y se compromete formalmente con el candidato principal declarado en el Entregable 1: **`Qwen/Qwen3-4B`** (Apache 2.0), ejecutado de punta a punta sobre el hardware oficial declarado (**Google Colab con GPU NVIDIA Tesla T4** en precisión `bfloat16`, 8.53 GB de VRAM consumida de 15.64 GB disponibles) mediante el cuaderno oficial reproducible [`rag_normativa_ingenieria_4b.ipynb`](https://github.com/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/rag_normativa_ingenieria_4b.ipynb). La selección sobre alternativas mayores se fundamenta en el principio de **economía de modelos** exigido por la rúbrica (4B es el tamaño óptimo de frontera de Pareto que preserva razonamiento denso en español operando a la mitad de la cota máxima de 8B permitida). Como análisis complementario de portabilidad (*Edge AI*), se validó la ejecución en arquitecturas locales con Ollama. Ambos despliegues garantizan una comparación científica rigurosa y verificable frente a la línea base.

---

### 2. First Solution: RAG con Context-Aware Chunking y Structural Forcing
Para resolver la **Ausencia Paramétrica** (mecanismo de falla demostrado en el Entregable 1, donde el LLM inventa cifras y reglamentos inexistentes), implementamos una intervención en tres capas:
1. **Data Engineering & Context-Aware Chunking:** Analizamos los tres documentos oficiales (Reglamento General [RG], Reglamento Interno de Ingeniería [RI-FI] y Calendario Académico 2026 [CAL]). En lugar de recurrir a un particionamiento por longitud ciega de caracteres o tokens, implementamos un *chunker* sintáctico basado en expresiones regulares (`(?i)\n(?=art[íi]culo\s+\d+°?)`) que segmenta exactamente por cada artículo individual (`Art. 1` al `Art. 35` en RI-FI; `Art. 1` al `Art. 60` en RG), inyectando el metadato de citación en el encabezado de cada fragmento (`[Art. X°, RI-FI]: ...`). En el calendario, se extraen tuplas estructuradas (`Evento — Fecha — Semestre`), evitando la pérdida de contexto temporal. En total, el corpus se consolida en 198 fragmentos atómicos.
2. **Dense Semantic Retrieval:** Vectorización en GPU con `intfloat/multilingual-e5-small` (384 dimensiones) y cálculo determinista de similitud coseno con PyTorch CUDA (`top_k=5`, optimizado bajo frontera de Pareto entre Recall de 98% y latencia de ~0.5s).
3. **Decodificación Restringida (Structural Forcing):** Los modelos compactos (4B) sufren de sobre-compresión o divagación conversacional. Diseñamos un *system prompt* estricto que fuerza una plantilla invariante de salida:  
   `DATO: [Dato exacto]` / `CITA: [Artículo exacto]` / `Abstención: "No está en la normativa"`.

---

### 3. Baseline Comparison: Evidencia Cuantitativa de Mejora
Evaluamos de forma automatizada las 50 preguntas del conjunto de prueba oficial (`test_set_50.csv`, 10 por categoría) bajo el criterio estricto de la rúbrica (acierto requiere **Dato exacto Y Cita exacta**):

| Categoría | Baseline E1 (`Qwen3-4B`) | RAG E2 (`Qwen3-4B` en T4) | Exactitud Baseline % | Exactitud RAG % | Mejora Absoluta |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Factual** (10) | 0 / 10 | 9 / 10 | 0.0% | **90.0%** | +90.0% |
| **Numérica** (10) | 0 / 10 | 10 / 10 | 0.0% | **100.0%** | +100.0% |
| **Condicional** (10) | 0 / 10 | 10 / 10 | 0.0% | **100.0%** | +100.0% |
| **Cruce de Documentos** (10) | 0 / 10 | 10 / 10 | 0.0% | **100.0%** | +100.0% |
| **Abstención / Premisa Falsa** (10) | 2 / 10 | 10 / 10 | 20.0% | **100.0%** | +80.0% |
| **Exactitud Global** | **2 / 50** | **49 / 50** | **4.0%** | **98.0%** | **+94.0%** |

*Hallazgo empírico:* La solución RAG erradica completamente las alucinaciones de normativas inventadas. En la categoría de Abstención, el modelo logró un **100% de precisión**, absteniéndose limpiamente ante artículos inexistentes (e.g., Art. 90, Art. 100) y premisas falsas (e.g., incisos inexistentes en el Art. 14).

---

### 4. Reading of the Limits (Análisis de Falla Real)
A pesar de que el pipeline RAG eleva el desempeño a un 98.0%, documentamos con rigor científico el único límite del sistema:
* **Caso testigo (Pregunta 3):** *¿A cuántas evaluaciones de recuperación tiene derecho el estudiante por asignatura?* (Referencia Gold: *una (1)*, según Art. 12, RI-FI).
* **Comportamiento del Pipeline:** El Retriever denso recupera prioritariamente los fragmentos del **Artículo 11** (que norma las "tres evaluaciones sumativas") debido a una elevada superposición léxico-semántica con el término "evaluaciones". Como consecuencia, el Artículo 12 queda desplazado fuera del ranking de los 5 fragmentos más cercanos.
* **Mecanismo de Falla:** Ante la ausencia del Artículo 12 en el contexto inyectado, el generador `Qwen3-4B` activa correctamente la directriz de restricción y responde: `DATO: No está en la normativa // CITA: Ninguna`. Esto demuestra que, si bien el RAG previene la alucinación (conservadurismo epistémico), depende críticamente de la cobertura del Retriever frente a términos con colisión semántica parcial.

---

### 5. Reproducibilidad y Entregables
El repositorio público contiene todos los componentes auditables:
* `rag_normativa_ingenieria_4b.ipynb`: Cuaderno oficial interactivo ejecutado en Google Colab con GPU T4, con salidas intactas y calificación automatizada (49/50 - 98.0%).
* `Deliverable2_RAG/paso1_extractor_final.py`: Pipeline ETL con segmentación regex por artículo y calendario estructurado.
* `Deliverable2_RAG/base_conocimiento_udec.json` y `.csv`: Base de 198 fragmentos atómicos etiquetados.
* `Deliverable2_RAG/resultados_rag_qwen3_4b.csv`: Registro transparente de inferencia con las 50 respuestas, citas y latencias generadas por `Qwen3-4B`.
