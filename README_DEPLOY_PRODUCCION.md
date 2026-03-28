# ChatBotPt - Deploy a Produccion

Guia de despliegue del chatbot Rasa + Action Server en Docker para entorno productivo.

## 1) Objetivo

Levantar en produccion:
- `rasa` (API + modelo NLU/Core)
- `actions` (custom actions)

Con comportamiento estable para intents criticos como:
- `me pega`
- `estoy en peligro`
- `hola`

## 2) Requisitos

- Docker Engine
- Docker Compose plugin (`docker compose`)
- Dominio (opcional pero recomendado)
- Reverse proxy (Nginx/Caddy) recomendado

## 3) Configuracion critica (muy importante)

## 3.1 Endpoint de acciones en `endpoints.yml`

Archivo: `endpoints.yml`

Debe quedar asi en este proyecto:

```yml
action_endpoint:
  url: "http://actions:5055/webhook"
```

No usar placeholders `${...}` aqui para este caso.
Motivo: esta fue la falla principal detectada; Rasa enviaba URL invalida y no ejecutaba `action_answer_violence_type`.

## 3.2 Montaje de `data` en contenedor `actions`

Archivo: `docker-compose.yml`

Asegura este volumen:

```yml
services:
  actions:
    volumes:
      - ./actions:/app/actions
      - ./data:/app/data:ro
```

Sin ese volumen, el action server no puede leer `data/tipos_violencia/*.json`.

## 3.3 Entrenamiento + recarga

Cada cambio en:
- `domain.yml`
- `data/nlu.yml`
- `data/rules.yml`
- `data/stories.yml`
- `actions/actions.py`

requiere:
1. entrenar modelo,
2. reiniciar `rasa`.

## 4) Deploy en servidor (Docker)

Desde la carpeta del proyecto:

```bash
docker compose up -d --build
docker compose exec rasa rasa train
docker compose restart rasa
```

Verificacion:

```bash
docker compose ps
docker compose logs rasa --tail 100
docker compose logs actions --tail 100
```

## 5) Exposicion segura

Publicar solo Rasa (`5005`) al exterior.
No publicar `5055` (actions) a internet.

Ejemplo recomendado:
- `https://chat.tudominio.com` -> `http://localhost:5005`

## 6) Smoke tests obligatorios

## 6.1 Parse de intent

```bash
curl -X POST https://chat.tudominio.com/model/parse \
  -H "Content-Type: application/json" \
  -d '{"text":"me pega"}'
```

Esperado: intent top `tipo_violencia_fisica`.

## 6.2 Webhook de conversacion

```bash
curl -X POST https://chat.tudominio.com/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender":"smoke_prod","message":"me pega"}'
```

Esperado: respuesta no vacia y especifica de violencia fisica.

## 6.3 Flujo minimo

1. `me pega`
2. `hola`
3. `estoy en peligro`
4. `gracias`

Esperado:
- 1: guia completa de violencia fisica
- 2: saludo normal
- 3: protocolo urgente
- 4: despedida

## 7) Troubleshooting rapido

1. `me pega` responde vacio:
- revisar `endpoints.yml`
- revisar logs de `rasa` por `InvalidURL`

2. Fallback generico en casos claros:
- verificar modelo activo en `/status`
- reentrenar y reiniciar `rasa`

3. Action server no encuentra informacion:
- verificar volumen `./data:/app/data:ro`

## 8) Comandos utiles

```bash
# estado
docker compose ps

# logs
docker compose logs rasa --tail 200
docker compose logs actions --tail 200

# retrain + reload
docker compose exec rasa rasa train
docker compose restart rasa

# reinicio total
docker compose down
docker compose up -d --build
```
