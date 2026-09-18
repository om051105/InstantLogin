# Multi-stage build for React frontend
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Serve static files (handled by Nginx in production via shared volume)
FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist

# Keep the container alive so the shared volume gets populated
CMD ["sh", "-c", "cp -r /app/dist/* /output/ && echo 'Frontend built and copied' && tail -f /dev/null"]
