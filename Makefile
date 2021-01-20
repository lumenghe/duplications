COMPOSE = docker-compose -p contentsquare


.PHONY: run
run:
	$(COMPOSE) build app
	$(COMPOSE) up app


.PHONY: down
down:
	$(COMPOSE) down --volumes


.PHONY: format
format:
	$(COMPOSE) build format-imports
	$(COMPOSE) run format-imports
	$(COMPOSE) build format
	$(COMPOSE) run format


.PHONY: check-format
check-format:
	$(COMPOSE) build check-format-imports
	$(COMPOSE) run check-format-imports
	$(COMPOSE) build check-format
	$(COMPOSE) run check-format


.PHONY: style
style: check-format
	$(COMPOSE) build style
	$(COMPOSE) run style

