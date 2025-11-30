FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	bash \
	curl \
	ca-certificates \
	git \
	&& rm -rf /var/lib/apt/lists/*

# Working dir
WORKDIR /workspace

# Copy only necessary files
COPY . /workspace

# Install Python requirements
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

# Expose metrics port
EXPOSE 8000

# Default command will start in watch mode
CMD ["python", "-m", "agent.agent_runner", "--watch"]
