############################
# Help
############################

.DEFAULT_GOAL := help
.PHONY: help vendor
help: ## Show help
	@echo "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:"
	@grep -E '^[a-zA-Z_/%\-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

############################
# Setup
############################

setup: environment vendor ## Prepare environment

environment:
	@echo "#### Install Ansible Python Dependencies"
	pip install --no-cache -r requirements.txt
