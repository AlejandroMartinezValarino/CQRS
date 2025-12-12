# Frontend CQRS Anime Analytics

Frontend React + TypeScript con Ant Design para el sistema CQRS de analytics de animes.

## Stack Tecnológico

- React 18 + TypeScript
- Vite
- Ant Design
- Apollo Client (GraphQL)
- Axios (REST API)
- React Router

## Instalación

```bash
cd frontend
npm install
```

## Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

## Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```
VITE_GRAPHQL_URL=http://localhost:8001/graphql
VITE_API_URL=http://localhost:8000
```

## Build

```bash
npm run build
```

## Docker

```bash
docker build -t cqrs-frontend .
docker run -p 80:80 cqrs-frontend
```

## Railway

El proyecto está configurado para Railway con:
- `Dockerfile` para build multi-stage
- `nixpacks.toml` como alternativa

Variables de entorno necesarias en Railway:
- `VITE_GRAPHQL_URL`: URL del GraphQL endpoint
- `VITE_API_URL`: URL del REST API
- `PORT`: Puerto asignado por Railway (automático)
