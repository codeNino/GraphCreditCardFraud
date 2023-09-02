# Makefile

# Define the default target (the one that gets executed when you run just "make" without any arguments).
# You can change this to the specific target name you want to run by default.
default: run

# Define the target to run the Docker Compose file.
run:
	sudo docker compose up  --build -d

# Define additional targets as needed. For example, if you want to stop the containers:
stop:
	sudo docker compose down

clean:
	sudo docker compose down -v --remove-orphans

# Add more targets and commands as needed based on your requirements.
# For example, you can add targets for building specific services, cleaning up, etc.

# You can also define variables to make your Makefile more flexible.
# For instance, if you want to specify a custom Docker Compose file, you can use a variable like this:
# COMPOSE_FILE := docker-compose.custom.yml
# And then use it in your targets:
# run:
#   docker-compose -f $(COMPOSE_FILE) up -d

# Additionally, you can define variables for other options like project name, environment variables, etc.

# Add a target to show the help text with available targets.
help:
	@echo "Available targets:"
	@echo "  run        : Start the Docker Compose services in detached mode."
	@echo "  stop       : Stop and remove the Docker Compose services."
	@echo "  help       : Show this help message."

# Makefile PHONY targets (targets that are not files but are used as commands).
.PHONY: default run stop clean help
