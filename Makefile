.PHONY: help install run test clean appimage

help:
	@echo "Pacman GUI - Makefile Commands"
	@echo ""
	@echo "make install    - Install dependencies"
	@echo "make run        - Run the application"
	@echo "make test       - Run tests"
	@echo "make clean      - Clean cache and build files"
	@echo "make appimage   - Build AppImage"
	@echo ""

install:
	@echo "Installing dependencies..."
	pip install --user -r requirements.txt

run:
	@echo "Starting Pacman GUI..."
	python3 main.py

test:
	@echo "Running tests..."
	bash test.sh

clean:
	@echo "Cleaning up..."
	rm -rf build/
	rm -rf __pycache__/
	rm -rf pacman_gui/__pycache__/
	rm -rf pacman_gui/*/__pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	rm -f ~/.cache/pacman-gui/packages.json

appimage:
	@echo "Building AppImage..."
	bash build_appimage.sh

quickstart:
	@cat QUICKSTART.md

.DEFAULT_GOAL := help
