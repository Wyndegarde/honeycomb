FROM node:24-alpine AS build-env
COPY . /app/
WORKDIR /app
RUN npm ci && npm run build

# SPA build: static files, with /api proxied to the backend (set API_URL at run time)
FROM nginx:alpine
ENV API_URL=http://backend:8000
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build-env /app/build/client /usr/share/nginx/html
