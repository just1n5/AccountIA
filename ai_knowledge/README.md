# Base de Conocimiento de IA - AccountIA

Esta carpeta contiene todos los documentos legales y fiscales que alimentan el sistema RAG (Retrieval-Augmented Generation) de AccountIA.

## Estructura

### `/documents`
Documentos fuente organizados por categoría:

#### `/estatuto_tributario`
- Artículos del Estatuto Tributario colombiano
- Actualizaciones anuales
- Decretos reglamentarios

#### `/dian_concepts`
- Conceptos unificados de la DIAN
- Interpretaciones oficiales
- Guías para contribuyentes

#### `/regulations`
- Decretos y resoluciones complementarias
- Ley 2277 de 2022 (Reforma tributaria)
- Otras normativas relevantes

### `/processed`
Documentos procesados para el sistema RAG:
- Chunks de texto fragmentados
- Embeddings vectoriales
- Índices de búsqueda

### `/scripts`
Scripts para procesamiento automatizado:
- `process_documents.py` - Fragmentación de documentos
- `create_embeddings.py` - Generación de embeddings
- `update_knowledge_base.py` - Actualización de la base

### `/config`
Configuraciones para el procesamiento:
- Parámetros de chunking
- Configuración de embeddings
- Configuración del sistema RAG

## Actualización de Contenido

Para mantener la base de conocimiento actualizada:

1. **Agregar nuevos documentos**: Colocar en la carpeta correspondiente en `/documents`
2. **Ejecutar procesamiento**: `python scripts/process_documents.py`
3. **Actualizar embeddings**: `python scripts/create_embeddings.py`
4. **Validar funcionamiento**: `python scripts/test_rag.py`

## Importante

- Verificar que todos los documentos sean de fuentes oficiales
- Mantener versionado de cambios normativos
- Documentar fechas de vigencia de cada norma
- Revisar calidad de las respuestas de IA periódicamente