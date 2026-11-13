# One entry point for everything that is run by hand: development, management commands, server operations.
#
#   make            list all targets
#   make <target>   run one, parameters are passed as NAME=value
#
# Management commands run locally (virtualenv, .env.dev) or inside the backend container of docker-compose.yaml.
# The container is used automatically on the server (where /etc/subtenancy/config/backend exists);
# force one or the other with DOCKER=1 or DOCKER=0.

SHELL := /bin/bash
.SHELLFLAGS := -euo pipefail -c
.DEFAULT_GOAL := help

# Parameters only count when given on the command line, never when they happen to be in the environment
# (EMAIL, USERNAME and the like often are).
PARAMS := USERNAME EMAIL FIRST_NAME LAST_NAME ROLE PASSWORD SUPERUSER PERSON PDF OUTPUT APPLY DRY_RUN CMD ARGS \
          REF ARCHIVE ADDR SERVICE
$(foreach v,$(PARAMS),$(if $(filter environment%,$(origin $(v))),$(eval $(v) :=)))

PYTHON ?= python3
DOCKER ?= $(if $(wildcard /etc/subtenancy/config/backend),1,0)

ifeq ($(DOCKER),1)
MODE := backend container
# -T when there is no terminal (cron, pipes), a TTY otherwise (shell, prompts)
EXEC := docker compose exec $$([ -t 0 ] && [ -t 1 ] || echo -T) backend
MANAGE := $(EXEC) python manage.py
else
MODE := local
ifneq ($(wildcard venv/bin),)
export PATH := $(CURDIR)/venv/bin:$(PATH)
endif
MANAGE := set -a && . ./.env.dev && set +a && python manage.py
endif

# $(call require,A B): fail unless the parameters A and B are given
require = $(foreach v,$(1),$(if $($(v)),,$(error $@ needs $(v)=..., see `make help`)))
# $(call flag,VAR,--option): the option if VAR=1
flag = $(if $(filter 1,$($(1))),$(2))
# $(call opt,VAR,--option): the option with the value of VAR if it is set (quoted by the shell, not by make)
opt = $(if $($(1)),$(2) "$$$(1)")

.PHONY: help
help: ## List all targets
	@awk 'BEGIN { FS = ":.*## " } \
	    /^##@ / { printf "\n\033[1m%s\033[0m\n", substr($$0, 5); next } \
	    /^[a-z-]+:.*## / { split($$2, d, " -- "); \
	        if (d[2] == "") printf "  \033[36m%-22s\033[0m %s\n", $$1, d[1]; \
	        else printf "  \033[36m%-22s\033[0m %s\n  %-22s \033[2m%s\033[0m\n", $$1, d[1], "", d[2] }' $(MAKEFILE_LIST)
	@printf '\nManagement commands run in: \033[1m%s\033[0m (override with DOCKER=1 or DOCKER=0)\n' '$(MODE)'

##@ Development

.PHONY: install dev test css css-watch messages
install: ## Create the virtualenv and install all dependencies, including Playwright's Chromium -- [PYTHON=python3.13]
	test -d venv || $(PYTHON) -m venv venv
	venv/bin/pip install -r requirements-dev.txt
	venv/bin/playwright install chromium

dev: ## Start the development server with .env.dev -- [ADDR=0.0.0.0:8000]
	scripts/develope.sh $(ADDR)

test: ## Run the tests -- [ARGS="-k contact -x"]
	pytest $(ARGS)

css: ## Rebuild the committed stylesheet with Tailwind
	scripts/build-css.sh

css-watch: ## Rebuild the stylesheet on every change
	scripts/build-css.sh --watch

messages: ## Compile the translations
	$(MANAGE) compilemessages

##@ Management commands

.PHONY: init migrate sync-groups create-account export-personal-data prune shell manage
init: ## Migrate, create the permission groups and the first superuser (prints its password) -- SUPERUSER=name EMAIL=address [PASSWORD=...]
	$(call require,SUPERUSER EMAIL)
	@$(MANAGE) init_database --superuser "$$SUPERUSER" --email "$$EMAIL" $(call opt,PASSWORD,--password)

migrate: ## Run the migrations and sync the permission groups
	$(MANAGE) migrate --no-input
	$(MANAGE) sync_groups

sync-groups: ## Reset the permission groups to tenants/groups.py -- [DRY_RUN=1]
	$(MANAGE) sync_groups $(call flag,DRY_RUN,--dry-run)

create-account: ## Create a staff account (prints its start password) -- USERNAME=name EMAIL=address FIRST_NAME=... LAST_NAME=... [ROLE=assistant|external] [PASSWORD=...]
	$(call require,USERNAME EMAIL FIRST_NAME LAST_NAME)
	@$(MANAGE) create_account "$$USERNAME" "$$EMAIL" --first-name "$$FIRST_NAME" --last-name "$$LAST_NAME" \
	    $(call opt,ROLE,--role) $(call opt,PASSWORD,--password)

export-personal-data: ## Export everything stored about one person (Art. 15 GDPR), JSON to stdout by default -- PERSON=username|email|id [PDF=file] [OUTPUT=file.json]
	$(call require,PERSON)
ifeq ($(DOCKER),1)
# the files are written on the host, not inside the container
ifneq ($(PDF),)
	@docker compose exec -T backend python manage.py export_personal_data "$$PERSON" --pdf /tmp/personal-data.pdf > /dev/null
	@docker compose cp backend:/tmp/personal-data.pdf "$$PDF"
	@docker compose exec -T backend rm -f /tmp/personal-data.pdf
	@echo "PDF written to $$PDF"
endif
ifneq ($(OUTPUT),)
	@docker compose exec -T backend python manage.py export_personal_data "$$PERSON" > "$$OUTPUT"
	@echo "JSON written to $$OUTPUT"
endif
ifeq ($(PDF)$(OUTPUT),)
	@docker compose exec -T backend python manage.py export_personal_data "$$PERSON"
endif
else
	@$(MANAGE) export_personal_data "$$PERSON" $(call opt,PDF,--pdf) $(call opt,OUTPUT,--output)
endif

prune: ## Delete stale accounts, contracts and PDFs; a dry run that only lists them unless APPLY=1 -- [APPLY=1]
ifeq ($(APPLY),1)
	@$(MANAGE) prune_stale_data --apply
else
# the dry run ends with an error on purpose (it rolls back), that is not a failure here
	@$(MANAGE) prune_stale_data || true
endif

shell: ## Open the Django shell
	@$(MANAGE) shell

manage: ## Run any other manage.py command -- CMD="changepassword admin"
	$(call require,CMD)
	@$(MANAGE) $(CMD)

##@ Server

.PHONY: up down ps logs deploy backup restore
up: ## Build and start the containers
	docker compose up -d --build

down: ## Stop the containers
	docker compose down

ps: ## Show the state of the containers
	docker compose ps

logs: ## Follow the logs -- [SERVICE=backend|database]
	docker compose logs -f --tail 100 $(SERVICE)

deploy: ## Check out a release, rebuild, restart, migrate and sync the groups -- [REF=v2.1.0], default main
	scripts/deploy.sh $(REF)

backup: ## Archive the database and the contract PDFs -- [BACKUP_DIR=/home/str3/backups]
	scripts/backup.sh

restore: ## Restore a backup archive into an empty installation -- ARCHIVE=file.tar.gz
	$(call require,ARCHIVE)
	scripts/restore.sh "$$ARCHIVE"
