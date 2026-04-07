# Stage 1: Build the React Application safely using node
FROM node:20-alpine AS builder

WORKDIR /app

# Explicitly copy deps securely
COPY package.json package-lock.json ./
RUN npm ci

# Copy logic mappings
COPY . .

# Generate optimized bundled definitions 
RUN npm run build

# Stage 2: Serve standard HTTP via optimized NGINX layer natively
FROM nginx:alpine

# Purge default configurations organically 
RUN rm -rf /usr/share/nginx/html/* && rm /etc/nginx/conf.d/default.conf

# Map build targets explicitly
COPY --from=builder /app/dist /usr/share/nginx/html

# Layer explicit configurations implicitly directing logic paths proxying correctly
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

# Validate core service listening organically checking generic 200 codes dynamically
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:3000 || exit 1

CMD ["nginx", "-g", "daemon off;"]
