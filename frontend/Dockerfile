FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG VITE_API_URL
ARG VITE_GRAPHQL_URL

ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_GRAPHQL_URL=${VITE_GRAPHQL_URL}

RUN npm run build

FROM nginx:alpine

RUN apk add --no-cache gettext

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Railway asigna PORT dinámicamente, exponemos ese puerto
EXPOSE ${PORT:-8080}

# No establecer PORT por defecto aquí, dejar que Railway lo asigne

CMD ["sh", "-c", "envsubst '$$PORT' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
