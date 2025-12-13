# Makefile for Cult of Azathoth

TEMPLATE_DIR := templates

ROOMS_TEMPLATE := $(TEMPLATE_DIR)/rooms.yaml.tpl
ITEMS_TEMPLATE := $(TEMPLATE_DIR)/items.yaml.tpl
GOALS_TEMPLATE := $(TEMPLATE_DIR)/goals.md.tpl
NOTES_TEMPLATE := $(TEMPLATE_DIR)/notes.md.tpl


PYTHON ?= python3

.PHONY: run clean scenario

# -------------------------
# Run the game
# Usage:
#   make run manor
#   make run            (defaults to manor)
# -------------------------
run:
	@SCEN="$(word 2,$(MAKECMDGOALS))"; \
	if [ -z "$$SCEN" ]; then \
	  SCEN="manor"; \
	fi; \
	echo "Running scenario '$$SCEN'"; \
	$(PYTHON) main.py --scenario "$$SCEN"

# Prevent make from treating extra words as targets
%:
	@:

# -------------------------
# Clean Python cache files
# -------------------------
clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} \; -o -name "*.pyc" -delete

# -------------------------
# Create a new scenario
# Usage:
#   make scenario name=village
# -------------------------
scenario:
	@SCEN="$(name)"; \
	if [ -z "$$SCEN" ]; then \
	  echo "Usage: make scenario name=<name>"; \
	  exit 1; \
	fi; \
	SCEN_DIR="dev/scenario_$$SCEN"; \
	if [ -e "$$SCEN_DIR" ]; then \
	  echo "Error: $$SCEN_DIR already exists. Aborting."; \
	  exit 1; \
	fi; \
	echo "Creating scenario in $$SCEN_DIR"; \
	mkdir -p "$$SCEN_DIR"; \
	cp "$(ROOMS_TEMPLATE)" "$$SCEN_DIR/rooms.yaml"; \
	cp "$(ITEMS_TEMPLATE)" "$$SCEN_DIR/items.yaml"; \
	cp "$(GOALS_TEMPLATE)" "$$SCEN_DIR/goals.md"; \
	cp "$(NOTES_TEMPLATE)" "$$SCEN_DIR/notes.md"; \
	echo "Scenario '$$SCEN' created."

