FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Copy the project into the image
ADD . /test-confidential

# Set the working directory
WORKDIR /test-confidential

# Sync the project into a new environment using the frozen lockfile
RUN uv sync --frozen

# Allow workload operator to override env variables
LABEL "tee.launch_policy.allow_env_override"="NONCE,AUDIENCE,TOKEN_TYPE"

# Define the entrypoint
ENTRYPOINT ["uv", "run", "attestation.py"]