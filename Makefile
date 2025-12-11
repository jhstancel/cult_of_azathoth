# Makefile for Cult of Azathoth

PYTHON ?= python

.PHONY: run clean

run:
	$(PYTHON) main.py

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} \; -o -name "*.pyc" -delete

