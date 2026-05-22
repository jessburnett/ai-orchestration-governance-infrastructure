FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Pre-install common dependencies
RUN pip install --no-cache-dir fastapi uvicorn langchain langchain-core requests streamlit pandas plotly

# Copy the toolkit source needed for installation
COPY toolkit/agent-governance-python/agent-os/ ./toolkit/agent-governance-python/agent-os/
COPY toolkit/agent-governance-python/agent-sre/ ./toolkit/agent-governance-python/agent-sre/

# Install the toolkit packages
RUN pip install --no-cache-dir ./toolkit/agent-governance-python/agent-os
RUN pip install --no-cache-dir ./toolkit/agent-governance-python/agent-sre

# Copy the ecosystem package + start script
COPY aogi/ ./aogi/
COPY scripts/start_stack.sh ./scripts/
RUN chmod +x scripts/start_stack.sh

EXPOSE 8000
EXPOSE 8501

CMD ["./scripts/start_stack.sh"]
