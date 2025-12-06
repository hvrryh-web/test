FROM ghcr.io/comfyanonymous/comfyui:${COMFYUI_TAG:-latest}

USER root
RUN apt-get update \ 
    && apt-get install -y --no-install-recommends git \ 
    && rm -rf /var/lib/apt/lists/*

# Install Z-Image utilities into custom nodes
RUN set -eux; \
    mkdir -p /opt/ComfyUI/custom_nodes; \
    if [ ! -d /opt/ComfyUI/custom_nodes/Comfyui-Z-Image-Utilities ]; then \
      git clone --depth=1 https://github.com/Koko-boya/Comfyui-Z-Image-Utilities /opt/ComfyUI/custom_nodes/Comfyui-Z-Image-Utilities; \
    fi

ENV HF_HOME=/models \
    COMFYUI_MODEL_DIR=/models

WORKDIR /opt/ComfyUI

CMD ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"]
