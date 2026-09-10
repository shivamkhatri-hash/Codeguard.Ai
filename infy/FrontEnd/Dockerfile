# Stage 1: Build React static assets with Vite
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Build Vite frontend bundle
RUN npm run build

# Stage 2: Serve static bundle with lightweight Nginx
FROM nginx:alpine

# Copy custom nginx config if available, or default to standard root static serve
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose HTTP port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
