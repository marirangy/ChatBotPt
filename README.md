# Nima Chatbot - ChatBotPt

<p align="center">
   Motor conversacional de Nima basado en Rasa para detección de riesgo, orientación y rutas de apoyo.
</p>

<p align="center">
   <img alt="Rasa" src="https://img.shields.io/badge/Rasa-3.6.x-5A17EE" />
   <img alt="Python" src="https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white" />
   <img alt="Docker" src="https://img.shields.io/badge/Container-Docker-2496ED?logo=docker&logoColor=white" />
   <img alt="Rasa SDK" src="https://img.shields.io/badge/Actions-Rasa%20SDK-0A0A0A" />
</p>

## Resumen

Este repositorio contiene el chatbot de Nima con dos componentes que trabajan en conjunto:

1. `rasa`: Core + NLU, API REST y manejo del diálogo.
2. `actions`: servidor de acciones personalizadas (`actions/actions.py`) con lógica y respuestas enriquecidas desde `data/tipos_violencia/`.

## Arquitectura

```text
[ Frontend Chat ]
         |
         v
[ Rasa Server :5005 ] -----> [ Action Server :5055 ]
         |                               |
         +-------------------------------+
                     lee conocimiento JSON
```

## Estructura principal

```text
ChatBotPt/
   actions/
      actions.py
   data/
      nlu.yml
      rules.yml
      stories.yml
      tipos_violencia/*.json
   domain.yml
   endpoints.yml
   config.yml
   docker-compose.yml
```

## Arranque rápido local

## Opción A: Docker (recomendada)

```bash
docker compose up -d
docker compose ps
```

Probar webhook:

```bash
curl -X POST http://localhost:5005/webhooks/rest/webhook \
   -H "Content-Type: application/json" \
   -d '{"sender":"local_test","message":"me pega"}'
```

## Opción B: Runtime local sin Docker

```bash
pip install -r requirements.txt
rasa train
```

Terminal 1:

```bash
rasa run actions
```

Terminal 2:

```bash
rasa run --enable-api --cors "*"
```

## Variables de entorno

Archivo `.env`:

```env
ACTION_ENDPOINT_URL=http://localhost:5055/webhook
```

Nota: para este proyecto en Docker, el valor operativo clave está en `endpoints.yml`.

## Configuración crítica (falla real detectada)

## 1) Endpoint de acciones

En `endpoints.yml` debe estar:

```yml
action_endpoint:
   url: "http://actions:5055/webhook"
```

No usar placeholders `${...}` aquí para este flujo en Docker, porque se detectó que podía quedar URL inválida y romper las respuestas de acciones.

## 2) Montaje de `data` en contenedor de actions

En `docker-compose.yml`:

```yml
services:
   actions:
      volumes:
         - ./actions:/app/actions
         - ./data:/app/data:ro
```

Si falta este volumen, las acciones no encuentran los JSON y el bot responde vacío o cae en fallback.

## Entrenamiento y ciclo de cambios

Si editas cualquiera de estos archivos:

- `domain.yml`
- `data/nlu.yml`
- `data/rules.yml`
- `data/stories.yml`
- `actions/actions.py`

ejecuta:

```bash
docker compose exec rasa rasa train
docker compose restart rasa
```

## Endpoints útiles

- Estado del modelo: `GET /status`
- Parse de texto: `POST /model/parse`
- Webhook chat: `POST /webhooks/rest/webhook`

## Smoke test recomendado

Validar este flujo mínimo:

1. `me pega`
2. `hola`
3. `estoy en peligro`
4. `gracias`

Esperado:

- detección de violencia física con respuesta completa.
- saludo normal.
- protocolo de urgencia.
- cierre/despedida.

## Troubleshooting rápido

1. `me pega` no responde:
- revisar `endpoints.yml`.
- revisar `docker compose logs rasa` por `InvalidURL`.

2. responde fallback en casos claros:
- verificar modelo activo en `/status`.
- reentrenar y reiniciar `rasa`.

3. actions no lee conocimiento:
- confirmar volumen `./data:/app/data:ro`.

## Producción

Guía completa de despliegue en:

- `README_DEPLOY_PRODUCCION.md`
