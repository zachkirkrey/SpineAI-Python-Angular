.PHONY: build backend frontend local local-bg

build: frontend backend

backend:
	(cd docker && docker-compose -f dev.docker-compose.yml build)

frontend:
	(cd frontend/docker && docker-compose build)

local:
	(cd docker && docker-compose -f local.docker-compose.yml up)

local-bg:
	(cd docker && docker-compose -f local.docker-compose.yml up -d)
