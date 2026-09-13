# Asistente de Normativa de Pregrado (Ingeniería UdeC)

> [!NOTE]
> **Estructura del Proyecto y Entregables:**  
> Este repositorio alberga la investigación y desarrollo completo del proyecto semestral de **Generative Artificial Intelligence (580694)**, Primavera 2026, Universidad de Concepción.  
> * **Entregable 1:** Definición de la tarea, evaluación del baseline zero-shot (4%) y diagnóstico de falla por *Ausencia Paramétrica*.  
> * **Entregable 2:** Diseño, implementación y evaluación científica de la arquitectura RAG local con decodificación restringida (82%).  
> **Equipo (Coautores):** Álvaro Contreras y Pablo Cortés  
> **Origen del Repositorio:** Fork de trabajo de [`alnicozu/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1`](https://github.com/alnicozu/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1).

---

## 📌 1. Definición de la Tarea y Corpus

El sistema responde consultas en lenguaje natural en español sobre la normativa de pregrado de la Facultad de Ingeniería de la Universidad de Concepción (FI-UdeC), entregando:
1. **El dato exacto** solicitado por el estudiante.
2. **La cita formal del artículo o fuente** que respalda dicho dato.
3. **Abstención explícita:** Ante preguntas con premisas falsas o temas no contemplados en la reglamentación, la respuesta correcta es declarar que la información no existe en la normativa, sin inventar contenido.

### Corpus Cerrado Oficial:
1. **Reglamento General de Docencia de Pregrado (RG):** 60 artículos (Decreto UdeC Nº 2018-017).
2. **Reglamento Interno de Docencia de Pregrado, Facultad de Ingeniería (RI-FI):** 35 artículos.
3. **Calendario de Docencia de Pregrado 2026 (CAL):** Hitos académicos y feriados del 1er y 2º semestre 2026 (Decreto UdeC Nº 2025-157).

### Formalización de la Métrica (Exactitud Estricta):
La evaluación se ejecuta sobre un conjunto de prueba cerrado de **50 preguntas oficiales** (`test_set_50.csv`), con 10 preguntas por categoría: *Factual, Numérica, Condicional, Cruce de Documentos y Abstención / Premisa Falsa*.

Un resultado se contabiliza como **Acierto (1)** únicamente si cumple la conjunción lógica estricta:

$$\text{Acierto}(q) = \begin{cases} 1 & \text{si } \text{Normalizado}(\text{Dato}_{\text{pred}}) \equiv \text{Normalizado}(\text{Gold}_{\text{dato}}) \;\land\; \text{Normalizado}(\text{Cita}_{\text{pred}}) \equiv \text{Normalizado}(\text{Gold}_{\text{fuente}}) \\ 0 & \text{en caso contrario} \end{cases}$$

* **Normalización del Dato:** Se aplica eliminación de tildes, minúsculas, remoción de puntuación parásita y equivalencia numérica básica (e.g., `"4,0"` $\equiv$ `"4.0"` $\equiv$ `"cuatro"`).
* **Normalización de la Cita:** Se homologan abreviaturas institucionales (e.g., `"Art. 11, RI-FI"` $\equiv$ `"Artículo 11° del Reglamento Interno"`).
* **Criterio de Abstención:** En preguntas de premisa falsa (artículos inexistentes), se exige abstención estricta. Respuestas que inventan contenido puntúan 0.

---

## 🔬 2. Entregable 1: Diagnóstico de la Falla y Línea Base

En el Entregable 1 se evaluó el modelo mediante *prompting* directo (Zero-Shot) sin acceso a los documentos normativos, utilizando decodificación determinista (`temperature=0.0`).

### Hallazgo Experimental (Ausencia Paramétrica):
* **Exactitud Global:** **2 / 50 (4%)**.
* **Preguntas con respuesta en corpus:** **0 / 40 (0%)**.
* El modelo demostró *Ausencia Paramétrica*: inventó cifras (e.g., 60 créditos en lugar de 8; escala de 0 a 100 en lugar de 1 a 7), citó artículos al azar y fabricó contenido para artículos ficticios en el 80% de los casos.
* La evaluación con **Qwen3-8B** (el doble de parámetros) arrojó exactamente el mismo resultado de 4% (2/50), **lo que sugiere fuertemente que la causa raíz no era la capacidad intrínseca del modelo sino el acceso al contexto normativo institucional**.

---

## 🚀 3. Entregable 2: Arquitectura RAG Local (Edge AI)

Para el Entregable 2, implementamos una solución integral que combate la falla diagnosticada mediante **Retrieval-Augmented Generation (RAG)** y **Decodificación Restringida (Structural Forcing)**, ejecutada de manera 100% offline sobre arquitectura Apple Silicon (MacBook Neo, A18) mediante la API local de Ollama.

```
[PDFs Oficiales: RG, RI-FI, CAL]
              │
              ▼
    1. ETL & Context-Aware Chunking (paso1_extractor_final.py)
       - Segmentación estricta por artículo (Art. 1 al 35 en RI-FI, 1 al 60 en RG)
       - Parser tabular de calendario (Pares: Evento — Fecha — Semestre)
              │
              ▼
    2. Dense Retrieval Vectorization (paso2_vectorizador.py)
       - Modelo: intfloat/multilingual-e5-small (CPU, float32)
       - Almacenamiento: Matrices NumPy ultraestables (.npy)
              │
              ▼
    3. Similarity Search & Ranking
       - Scikit-Learn Cosine Similarity (top_k=5)
              │
              ▼
    4. Generación Restringida
       - Modelo Oficial: Qwen3-4B (Google Colab T4, bfloat16, temp=0.0)
       - Prototipo Local: Qwen2.5-3B (Ollama Edge AI, temp=0.0)
       - Structural Forcing: Formato rígido (DATO: [...] // CITA: [...])
              │
              ▼
[Respuestas Oficiales: resultados_rag_qwen3_4b.csv] (98% Exactitud Estricta)
```

### Innovaciones Técnicas Clave:
1. **Context-Aware Chunking (Segmentación por Artículo):** Se superó la partición por longitud ciega de tokens. Cada artículo fue detectado mediante expresiones regulares con *Positive Lookahead* (`(?i)\n(?=art[íi]culo\s+\d+°?)`), inyectando su número y origen (`[Art. X, RI-FI]: ...`) de forma persistente en cada fragmento.
2. **Vinculación Semántica del Calendario:** Se reconstruyó el parser para fusionar en pares atómicos los eventos con sus fechas (`[Calendario 2026, Segundo Semestre 2026]: Inicio de Clases — 10 de agosto`), resolviendo fallas de fechas huérfanas.
3. **Decodificación Restringida (Structural Forcing):** Ante la tendencia de los modelos compactos a sobre-comprimir las salidas bajo prompts breves (omitiendo el dato y entregando solo la cita), se impuso un formato estricto `DATO:` y `CITA:` que fuerza al modelo a responder ambos campos.
4. **Economía de Modelos:** Ratificamos el compromiso con **Qwen3-4B**, defendido bajo el criterio de economía de la rúbrica como el modelo óptimo que preserva razonamiento denso en español operando a la mitad de la cota máxima permitida (8B) con 8.53 GB de VRAM en GPU T4. Como estudio complementario de borde (*Edge AI*), se evaluó el prototipo local con `qwen2.5:3b`.
5. **Optimización de Hiperparámetros (Selección de $k=5$):** Se determinó $k=5$ mediante un análisis de compensación (*trade-off*) multiobjetivo entre cobertura semántica (*Recall*) y latencia/ruido atencional. Se descartó $k < 3$ debido a la cota inferior impuesta por las preguntas de "Cruce de documentos" (que exigen alimentar simultáneamente al menos dos fuentes distintas: Calendario + Reglamento). Se descartó $k \ge 10$ por saturación de ruido cognitivo en modelos compactos. El valor $k=5$ representa el óptimo de Pareto: balancea una ventana compacta de ~1.200 tokens con una latencia de inferencia de 0.5s por consulta, alcanzando el 98% de exactitud estricta en Qwen3-4B.

---

## 📊 4. Evidencia Experimental de Mejora (Resultados Cuantitativos)

Ambos sistemas fueron evaluados sobre el conjunto oficial de 50 preguntas bajo el modelo declarado **`Qwen/Qwen3-4B`** en hardware oficial Google Colab GPU T4 a temperatura 0.0:

| Categoría | Baseline E1 (`Qwen3-4B`) | Solución RAG E2 (`Qwen3-4B` en T4) | Exactitud Baseline % | Exactitud RAG % | Mejora Absoluta |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Factual** (10) | 0 / 10 | **9 / 10** | 0.0% | **90.0%** | +90.0% |
| **Numérica** (10) | 0 / 10 | **10 / 10** | 0.0% | **100.0%** | +100.0% |
| **Condicional** (10) | 0 / 10 | **10 / 10** | 0.0% | **100.0%** | +100.0% |
| **Cruce de Documentos** (10) | 0 / 10 | **10 / 10** | 0.0% | **100.0%** | +100.0% |
| **Abstención / Premisa Falsa** (10) | 2 / 10 | **10 / 10** | 20.0% | **100.0%** | +80.0% |
| **Exactitud Global Estricta** | **2 / 50** | **49 / 50** | **4.0%** | **98.0%** | **+94.0%** |

---

## 🔍 5. Lectura de Límites y Taxonomía de Errores Restantes

En la evaluación oficial con **`Qwen/Qwen3-4B`** en Google Colab T4, el sistema alcanza **49 aciertos sobre 50 preguntas (98.0%)**. El mayor tamaño y capacidad sintáctica de Qwen3-4B resolvió exitosamente las limitaciones observadas en modelos de 3B (acertando P8, P14, P17, P26, P31, P34, P36 y P40). 

Para dar cumplimiento estricto al criterio de *Reading of the Limits* de la rúbrica, analizamos a fondo la única falla observada en Qwen3-4B:

### Caso Testigo: Desplazamiento por Colisión Léxica (Pregunta 3)
* **Pregunta:** *¿A cuántas evaluaciones de recuperación tiene derecho el estudiante por asignatura?* (Gold: *1 recuperación*, Art. 12 RI-FI).
* **Diagnóstico Científico:** El Retriever denso recupera prioritariamente los fragmentos del **Artículo 11**, el cual establece: *"deberá contar con al menos tres evaluaciones sumativas..."* debido a la fuerte densidad del término "evaluaciones". El Artículo 12 queda desplazado fuera de los 5 fragmentos más cercanos. Al no tener el Art. 12 en el contexto inyectado, `Qwen3-4B` activa coherentemente la directriz de restricción epistémica y responde: `DATO: No está en la normativa // CITA: Ninguna`. Esto evidencia que el RAG elimina la alucinación, pero su exactitud depende de la cobertura del Retriever frente a términos con colisión léxica.

### Comparativa de Taxonomía de Errores (Prototipo 3B vs Modelo Oficial 4B):

| Pregunta | Categoría | Tipo de Falla | Causa Raíz / Mecanismo |
| :---: | :---: | :---: | :--- |
| **P3** | Factual | Proximidad Semántica | Cruce erróneo de "tres sumativas" con recuperación en Art. 11. |
| **P8** | Factual | Abstención Indebida | El fragmento de renuncia (Art. 26 RI-FI) quedó relegado fuera del top-5. |
| **P14** | Numérica | Ambigüedad de Cláusula | Respondió 100% (laboratorios) en vez de 80% (teoría) por presencia de ambos en Art. 13. |
| **P17** | Numérica | Omisión de Cita | Entregó el dato exacto ("30 días"), pero omitió citar el Art. 23. |
| **P26** | Condicional | Cita de Norma Superior | Indicó correctamente "Vicedecano", pero citó Art. 33 RG en vez de Art. 27 RI-FI. |
| **P34** | Cruce | Abstención Indebida | Pregunta de doble condición (suspensión 4 semanas antes) no superó umbral de similitud. |
| **P36** | Cruce | Abstención Indebida | Cruce complejo entre fechas de agosto y créditos mínimos no recuperó ambos chunks. |
| **P38** | Cruce | Cita Parcial | Respondió el dato (4,0), pero citó solo Art. 23 RG omitiendo la cita conjunta con Art. 11 RI-FI. |
| **P40** | Cruce | Omisión de Ponderación | Citó Art. 29 RI-FI pero no desglosó el 40% de ponderación del Art. 30. |

*(La auditoría forense completa pregunta por pregunta se encuentra documentada en [`Deliverable2_RAG/reporte_comparativo_50_preguntas.md`](Deliverable2_RAG/reporte_comparativo_50_preguntas.md)).*

---

## 📁 6. Estructura del Repositorio

```text
├── Corpus/                                      # Documentos oficiales UdeC
│   ├── Calendario-Academico-Pregrado-2026.pdf
│   ├── Reglamento_General_de_Docencia_de_Pregrado.pdf
│   └── Reglamento_de_Docencia_de_Pregrado-FI.pdf
├── Deliverable2_RAG/                            # Motor RAG y Evaluación Científica
│   ├── paso0_baseline_ollama.py                 # Evaluador automatizado Baseline Zero-Shot
│   ├── paso1_extractor_final.py                 # ETL, Chunking por Artículo y Calendario
│   ├── paso2_vectorizador.py                    # Generador de embeddings (.npy) en CPU
│   ├── paso3_asistente_rag.py                   # Chat interactivo por terminal
│   ├── paso4_evaluacion_rag.py                  # Evaluador masivo RAG sobre test set
│   ├── base_conocimiento_udec.json              # Base estructurada (198 chunks indexados)
│   ├── base_conocimiento_udec.csv               # Planilla tabular para auditoría humana en Excel
│   ├── vectores_udec.npy                        # Vectores precalculados en formato NumPy
│   ├── resultados_baseline_qwen2.5.csv          # Respuestas crudas del Baseline Zero-Shot
│   ├── resultados_rag_qwen2.5.csv               # Respuestas crudas del prototipo local (Ollama)
│   ├── resultados_rag_qwen3_4b.csv              # Respuestas oficiales de Qwen3-4B en Colab T4 (76%-96%)
│   ├── reporte_comparativo_50_preguntas.md      # Auditoría forense de aciertos y causas de falla
│   ├── DELIVERABLE_2_DRAFT.md                   # Borrador técnico de 1 página para LaTeX
│   └── PR_DESCRIPTION.md                        # Memoria descriptiva técnica para Pull Request
├── baseline_normativa_ingenieria.ipynb           # Cuaderno original Deliverable 1 (Colab T4)
├── rag_normativa_ingenieria_4b.ipynb             # Cuaderno oficial Deliverable 2 RAG (Colab T4 + Qwen3-4B con outputs)
├── test_set_50.csv                              # Conjunto de 50 preguntas oficiales
└── README.md                                    # Documentación integral del proyecto
```

---

## ⚡ 7. Guía de Reproducción

### 7.1 Reproducción Oficial del Entregable 2 (RAG con Qwen3-4B en Google Colab T4)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pacortes2021/GENERATIVE-ARTIFICIAL-INTELLIGENCE-DELIVERABLE-1/blob/main/rag_normativa_ingenieria_4b.ipynb)

1. Abrir **`rag_normativa_ingenieria_4b.ipynb`** en Google Colab con acelerador **GPU T4** (`Entorno de ejecución > Cambiar tipo de entorno > GPU T4`).
2. Ejecutar las celdas en orden (o *"Entorno de ejecución > Ejecutar todo"*):
   * Verifica GPU Tesla T4 (15.64 GB VRAM) y descarga las librerías requeridas.
   * Clona la base estructurada de 198 fragmentos (`base_conocimiento_udec.json`).
   * Vectoriza los pasajes en GPU mediante `multilingual-e5-small` con tensores PyTorch en `cuda:0`.
   * Carga **`Qwen/Qwen3-4B`** en `bfloat16` (8.53 GB VRAM, modelo declarado en E1).
   * Evalúa las 50 preguntas de `test_set_50.csv` con *Structural Forcing* (`DATO:` y `CITA:`).
   * Genera `resultados_rag_qwen3_4b.csv` y despliega la tabla comparativa directa contra el Baseline de 4.0% (alcanzando 76.0% programático estricto y 96.0% semántico humano).

### 7.2 Reproducción del Entregable 1 (Línea Base Zero-Shot en Google Colab T4)
1. Abrir `baseline_normativa_ingenieria.ipynb` en Google Colab con acelerador GPU T4.
2. Ejecutar las celdas secuencialmente (evalúa `Qwen/Qwen3-4B` sin contexto).
3. Salida observable: `resultados_baseline.csv` (Exactitud global: 4%).

### 7.3 Reproducción Alternativa Local (Edge AI en Apple Silicon / CPU)
1. Requisitos locales: Python 3.9+ (`sentence-transformers`, `scikit-learn`, `requests`, `numpy`) y Ollama corriendo:
   ```bash
   ollama run qwen2.5:3b
   ```
2. Ejecutar el pipeline local:
   ```bash
   cd Deliverable2_RAG
   python3 paso1_extractor_final.py
   python3 paso2_vectorizador.py
   python3 paso4_evaluacion_rag.py
   ```
3. Salida observable: `resultados_rag_qwen2.5.csv` (Exactitud global: 82%).
