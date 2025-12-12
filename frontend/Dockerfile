FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

RUN apk add --no-cache gettext

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80

ENV PORT=80

CMD ["sh", "-c", "envsubst '$$PORT' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
