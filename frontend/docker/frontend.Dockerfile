# This Docker image provides the SpineAI frontend.

FROM node:12.16.1-buster

VOLUME /upload
VOLUME /etc/letsencrypt

# Install Angular dependencies
WORKDIR /app/angular
COPY angular/package.json ./
RUN npm install

# Install Express dependencies
WORKDIR /app/express
COPY express/package.json ./
RUN npm install

# Build Angular
WORKDIR /app/angular
COPY angular/angular.json ./
COPY angular/tsconfig.json ./
COPY angular/tsconfig.base.json ./
COPY angular/src ./src
RUN npm run-script build -- --prod

# Start Express
WORKDIR /app/express
RUN mkdir -p /app/express/upload
COPY express/services ./services
COPY express/config ./config
COPY express/app.js ./app.js

ENV NODE_ENV docker-dev
ENTRYPOINT ["npm", "run", "start"]
