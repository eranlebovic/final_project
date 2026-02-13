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
# Clean the default Nginx directory
RUN rm -rf /usr/share/nginx/html/*
# Copy the DIST folder from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
