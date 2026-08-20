# EPIData Fitness: Cognitive Brain API 🧠🚀

![Estado](https://img.shields.io/badge/Estado-Producci%C3%B3n-success)
![Framework](https://img.shields.io/badge/Framework-FastAPI-009688)
![Lenguaje](https://img.shields.io/badge/Lenguaje-Python%203.10+-3776AB)
![Seguridad](https://img.shields.io/badge/Seguridad-OWASP%20LLM%20Top%2010-red)

## 📌 Descripción del Microservicio

Este repositorio contiene el **Backend Cognitivo** (API RESTful) del proyecto *Entrenador Personal Inteligente y Biomecánico*. Construido sobre **FastAPI**, su propósito es recibir telemetría deportiva extrema (acelerometría, fatiga TSB, cadencia) desde el cliente Android, sanitizar los datos, y orquestar a los grandes modelos de lenguaje (Gemini 1.5 Pro y Llama 3.1) para emitir diagnósticos y planes de entrenamiento adaptativos.

El servidor actúa como un escudo protector (Gatekeeper) entre el usuario final y la inteligencia artificial, garantizando que el razonamiento cognitivo (ReAct) respete las reglas médicas y de ciberseguridad.

---

## 🛠️ Stack Tecnológico

- **Core & Enrutamiento:** FastAPI (Asincronía nativa y alto rendimiento).
- **Validación de Datos:** Pydantic (Modelado estricto y tipado estático).
- **Base de Datos NoSQL:** MongoDB + Motor (Driver asíncrono oficial).
- **Autenticación (AuthZ/AuthN):** Firebase Admin SDK (Validación de tokens JWT).
- **Inteligencia Artificial:** SDK oficial de Google GenAI (Gemini) y REST API (Groq).
- **Observabilidad (MLOps):** Librería `logging` configurada con `JsonFormatter` para compatibilidad ELK/Datadog.

---

## 🛡️ Arquitectura de Ciberseguridad y MLOps

A diferencia de un simple proxy de API, este backend incorpora defensas industriales de grado de producción:

### 1. OWASP LLM Mitigation (Anti-Prompt Injection)
Todas las descripciones cualitativas y feedback en texto libre enviados por el atleta pasan por el motor `sanitize_prompt_input`. Utilizando expresiones regulares (Regex), el backend neutraliza comandos invasivos como `"ignore all previous instructions"` o caracteres de escape de código, asegurando que el LLM nunca sea secuestrado.

### 2. Bucle Anti-Oscilación (Safety Fallback)
Si Gemini o Groq experimentan intermitencias en la red, alucinaciones o devuelven un JSON malformado, el backend aplica un límite duro de 3 reintentos. Al fallar, el servidor corta la conexión e inyecta un *Fallback de Seguridad* en memoria, recetando "Recuperación Activa en Zona 1" para garantizar la disponibilidad del servicio (100% Uptime).

### 3. Constrained Decoding (JSON Estricto)
Los LLMs están limitados por hardware a responder únicamente en base a los modelos Pydantic (`schema_class.schema_json()`). El comportamiento de chatbot ha sido erradicado, transformando a la IA en un micro-analista de datos.

### 4. Logging Estructurado JSON
Todos los logs de la terminal han sido migrados a formato JSON puramente estructurado (`JsonFormatter`), facilitando la ingesta forense e histórica de auditorías.

---

## 🚀 Guía de Instalación y Despliegue Local

### 1. Requisitos
- Python 3.10 o superior.
- Credenciales de [Google AI Studio](https://aistudio.google.com/) (Gemini).
- Credenciales de [Groq Console](https://console.groq.com/) (Llama 3.1).
- Archivo `firebase-credentials.json` provisto por la consola de Firebase.

### 2. Configuración del Entorno Virtual

Clona el repositorio e inicializa tu entorno aislado:

```bash
# Navegar al backend
cd picanteAvanzadoBackend

# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate  # En Linux/macOS
# venv\Scripts\activate   # En Windows
```

### 3. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### 4. Variables de Entorno (.env)

Crea un archivo llamado `.env` en la raíz de esta carpeta y define tus secretos:

```env
GEMINI_API_KEY=tu_clave_de_google_aqui
GROQ_API_KEY=tu_clave_de_groq_aqui
GROQ_MODEL=llama-3.1-70b-versatile
MONGO_URI=mongodb://localhost:27017/ # O tu clúster de MongoDB Atlas
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

### 5. Iniciar el Servidor (Uvicorn)

Ejecuta el servidor en modo desarrollo (recarga automática al cambiar código):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> **Verificación:** Visita `http://localhost:8000/docs` para ver la documentación interactiva Swagger UI auto-generada por FastAPI. 

---
*Este módulo backend fue diseñado con orgullo aplicando los estándares arquitectónicos y de ciberseguridad (U01 a U10) requeridos para el proyecto final EPIData Fitness.*
