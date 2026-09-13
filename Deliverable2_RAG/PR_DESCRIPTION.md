# Pull Request: Entrega Oficial Deliverable 2 — RAG Normativa Pregrado FI-UdeC

## 📌 Resumen Ejecutivo
Este Pull Request consolida la solución oficial para el **Entregable 2 (20%)**, cumpliendo rigurosamente con los 6 criterios de evaluación de la rúbrica del curso (Continuidad con E1, Ejecución demostrada en hardware declarado, Evidencia empírica de mejora, Lectura de límites, Economía de modelos y Reproducibilidad).

La arquitectura RAG eleva la exactitud estricta desde un **4.0% (2/50)** en el Baseline Zero-Shot hasta un **98.0% (49/50)** sobre el modelo declarado **`Qwen/Qwen3-4B`** en hardware oficial **Google Colab con GPU NVIDIA Tesla T4** (`bfloat16`).

---

## 🛠️ Modificaciones y Componentes Incluidos

### 1. Cuaderno Oficial Reproducible (`rag_normativa_ingenieria_4b.ipynb`)
- Cuaderno interactivo con salidas de ejecución intactas.
- Verificación de GPU Tesla T4 (15.64 GB VRAM) y consumo real de 8.53 GB de VRAM.
- Carga de `intfloat/multilingual-e5-small` en `cuda:0` y vectorización en <1s.
- Celda 13: Demostración en vivo con contraste explícito del Baseline alucinando Art. 8 vs RAG citando Art. 11°.
- Celda 17: Evaluación de las 50 preguntas arrojando la tabla de 98.0% (49/50).
- Celda 19: Caso de límite real (*Reading of the Limits*) en Pregunta 3.

### 2. Data Engineering & Context-Aware Chunking (`Deliverable2_RAG/paso1_extractor_final.py`)
- Segmentación regex con *lookahead* (`(?i)\n(?=art[íi]culo\s+\d+°?)`) que captura los 35 artículos de Ingeniería y 60 de Reglamento General sin fracturar artículos.
- Extracción de pares estructurados para el Calendario 2026 (`Evento — Fecha — Semestre`).
- Base de conocimiento consolidada de 198 fragmentos atómicos etiquetados (`base_conocimiento_udec.json` y `.csv`).

### 3. Trazabilidad Científica y Datos de Evaluación
- `Deliverable2_RAG/resultados_rag_qwen3_4b.csv`: Planilla completa con las 50 respuestas, citas normativas y latencias generadas por `Qwen3-4B` en T4.
- `Deliverable2_RAG/reporte_comparativo_50_preguntas.md`: Auditoría forense detallada fila por fila comparando Referencia Gold vs Baseline vs RAG.
- `Deliverable2_RAG/deliverable2.tex`: Documento técnico de 1 página en formato LaTeX a doble columna con diagrama de flujo vectorial TikZ integrado.

### 4. Documentación Exhaustiva (`README.md`)
- Doble guía de reproducción: oficial en Google Colab con badge interactivo y alternativa local offline con Ollama en Apple Silicon.
- Formalización matemática de la métrica estricta (Dato exacto $\land$ Cita exacta).
- Justificación multiobjetivo de $k=5$ bajo frontera de Pareto.
- Taxonomía y diagnóstico causal del caso de límite en Pregunta 3.

---

## ✅ Checklist de Cumplimiento de Rúbrica
- [x] **Continuidad con E1 (10 pts)**: Mismo objetivo, misma normativa, mismo test set oficial de 50 preguntas.
- [x] **Ejecución Demostrada (10 pts)**: Pipeline end-to-end en Google Colab GPU T4 con contraste del Baseline en la Celda 13.
- [x] **Evidencia de Mejora (10 pts)**: Salto cuantificable medido de 4.0% a 98.0% sobre 50 preguntas.
- [x] **Lectura de Límites (10 pts)**: Diagnóstico de colisión léxica en la Pregunta 3 (Art. 11 vs Art. 12).
- [x] **Economía de Modelos (10 pts)**: Elección de `Qwen3-4B` defendida como el modelo más pequeño funcional.
- [x] **Reproducibilidad y Repositorio (10 pts)**: Código abierto, rutas relativas, dependencias declaradas y badge de Colab funcional.
