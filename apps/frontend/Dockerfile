# STAGE 1: Build
FROM node:20-alpine AS build
WORKDIR /app
# Copy package files first to leverage Docker cache
COPY package*.json ./
RUN npm install
# Copy the rest of the code
COPY . .
# Explicitly run the build
RUN npm run build

# STAGE 2: Production (Nginx)
FROM nginx:alpine

# Configure nginx to run as non-root
RUN rm -rf /usr/share/nginx/html/* && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid /usr/share/nginx/html /var/cache/nginx /var/log/nginx /etc/nginx/conf.d && \
    sed -i 's/listen  *80;/listen 8080;/g' /etc/nginx/conf.d/default.conf

# Copy the DIST folder from the build stage
COPY --chown=nginx:nginx --from=build /app/dist /usr/share/nginx/html

USER nginx

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
