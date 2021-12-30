# This Docker image provides the SpineAI frontend.

FROM node:12.16.1-buster

VOLUME /database

WORKDIR /app/restify
COPY restify/package.json ./
RUN npm install

COPY restify/app.js ./
COPY restify/index.js ./
COPY restify/api ./api
COPY restify/models ./models
COPY restify/config ./config

ENV NODE_ENV docker-dev
ENTRYPOINT ["npm", "run", "start"]
