default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9_-]+:.*#' Makefile \
		| while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: freeze
freeze: # Freeze all requirements.
	pip freeze > requirements.txt

.PHONY: run
run: # Run the app locally
	python -m streamlit run src/app.py

.PHONY: build-docker
build-docker: # Build the app Docker image.
	docker build -t edu-llm-smm .

.PHONY: run-docker
run-docker: # Run the app in Docker container.
	docker run --rm -p 8501:8501 edu-llm-smm