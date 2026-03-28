# Nima - Chatbot (Rasa)
Motor inteligente NLU (Natural Language Understanding) construido y entrenado con **Rasa Open Source** para gestionar fluidamente las conversaciones en la plataforma web y ofrecer protocolos precisos.

## Componentes del Chatbot
Este proyecto utiliza dos procesos clave para funcionar correctamente que deben estar levantados simultáneamente:
1.  **Rasa Server**: Maneja la interpretación de entidades, intenciones de lenguaje natural y el historial del diálogo (Core y NLU).
2.  **Rasa Custom Action Server (`actions/`)**: Servidor Python interno en el puerto 5055 que procesa toda lógica compleja. Su archivo principal `actions/actions.py` inyecta respuestas ricas de las bases de conocimiento ubicadas en minería JSON (`data/tipos_violencia/`).

## Configuración Local (.env)
1. Para comenzar, clona el repositorio y activa tu entorno virtual de conda o venv.
2. Copia tu plantilla a `.env` final:
   ```bash
   cp .env.example .env
   ```
3. Instala dependencias si no las tenías (`pip install -r requirements.txt`).

## Ejecución y Entrenamiento
**Paso 1: Entrenar el modelo (Solo si modificaste historias o dominio)**
```bash
rasa train
```

**Paso 2: Levantamiento General (Obligatorio 2 terminales)**

Terminal A (Action Server):
```bash
rasa run actions
```

Terminal B (Core Server habilitando el Webhook):
```bash
rasa run --enable-api --cors "*"
```

## Variables de Entorno (`.env`)
*   `ACTION_ENDPOINT_URL`: La URL del action server. En local es `http://localhost:5055/webhook`. Es leída por el `endpoints.yml` al arrancar.
