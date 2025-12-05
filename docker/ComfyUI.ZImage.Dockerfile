# syntax=docker/dockerfile:1.6
FROM ghcr.io/comfyanonymous/comfyui:latest

# Install placeholder Z-Image Turbo assets and copy workflows
RUN --mount=type=cache,target=/root/.cache/comfyui/models \
    mkdir -p /opt/z-image-turbo && \
    echo "placeholder z-image turbo runtime" > /opt/z-image-turbo/README.txt

COPY resources/comfy /opt/comfyui/workflows/z-image

ENV COMFYUI_PORT=8188
EXPOSE 8188

CMD ["/bin/bash", "-lc", "python main.py --listen 0.0.0.0 --port ${COMFYUI_PORT}"]
