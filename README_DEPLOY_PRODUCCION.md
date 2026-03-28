# ChatBotPt - Deploy a Produccion (Render)

Guia para desplegar el chatbot en **Render** y conectarlo con frontend/backend en Vercel.

## 1) Objetivo

Publicar en Render:

1. Servicio `actions` (Rasa SDK)
2. Servicio `rasa` (Rasa API)

Con respuestas estables para intents criticos: `me pega`, `estoy en peligro`, `hola`.

## 2) Requisitos

- Cuenta en Render
- Repo `ChatBotPt` accesible por Render
- Un modelo entrenado disponible en `models/` o entrenamiento en pipeline

## 3) Configuracion critica por falla detectada

La falla historica fue `InvalidURL` al llamar actions. Para Render, evita endpoint interno de Docker y usa URL publica del servicio de actions.

## 3.1 Configurar archivo `endpoints.render.yml`

Contenido recomendado:

```yml
action_endpoint:
  url: "https://<tu-actions-render>.onrender.com/webhook"
```

Nota:

- Ya se incluye `endpoints.render.yml` en este repo.
- En local Docker puedes mantener `endpoints.yml` con `http://actions:5055/webhook`.
- En Render usa `endpoints.render.yml` para Rasa.

## 4) Crear servicio `actions` en Render

1. New Web Service -> repo `ChatBotPt`.
2. Name: `nima-actions`.
3. Environment: Docker (o nativo Python si prefieres).
4. Start command:

```bash
rasa run actions --port $PORT
```

5. Render expone `PORT` automaticamente.

Verificacion:

```bash
GET https://<tu-actions-render>.onrender.com/health
```

## 5) Crear servicio `rasa` en Render

1. New Web Service -> repo `ChatBotPt`.
2. Name: `nima-rasa`.
3. Start command recomendado:

```bash
rasa run --enable-api --cors "*" --port $PORT --endpoints endpoints.render.yml
```

4. Si el modelo no esta listo en build, entrena antes de desplegar o agrega etapa de entrenamiento en pipeline.

Verificacion:

```bash
GET https://<tu-rasa-render>.onrender.com/status
```

## 6) Integracion con Vercel (PaginaNima)

En el frontend de Vercel (`PaginaNima/frontend`):

```env
VITE_RASA_URL=https://<tu-rasa-render>.onrender.com/webhooks/rest/webhook
```

Luego redeploy frontend.

## 7) Smoke tests obligatorios

## 7.1 Parse de intent

```bash
curl -X POST https://<tu-rasa-render>.onrender.com/model/parse \
  -H "Content-Type: application/json" \
  -d '{"text":"me pega"}'
```

Esperado: intent top `tipo_violencia_fisica`.

## 7.2 Webhook

```bash
curl -X POST https://<tu-rasa-render>.onrender.com/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender":"smoke_prod","message":"me pega"}'
```

Esperado: respuesta no vacia y especifica (no fallback generico).

## 7.3 Flujo minimo

1. `me pega`
2. `hola`
3. `estoy en peligro`
4. `gracias`

## 8) Troubleshooting rapido

1. Error `InvalidURL` en logs de Rasa:
- revisar que `rasa` use `--endpoints endpoints.render.yml`.
- verificar URL publica correcta de `actions`.

2. `me pega` responde vacio:
- revisar logs de `actions` y permisos de lectura de `data/tipos_violencia`.

3. fallback excesivo:
- verificar modelo activo (`/status`).
- reentrenar y redeploy.

## 9) Integracion final recomendada

- Chatbot: Render
- Frontend: Vercel
- Backend: Vercel
- DB: MongoDB Atlas

Con esta combinacion, recuerda ajustar siempre en frontend:

```env
VITE_API_URL=https://<backend-vercel>.vercel.app
VITE_RASA_URL=https://<rasa-render>.onrender.com/webhooks/rest/webhook
```
