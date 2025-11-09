FROM nvidia/cuda:12.3.2-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY code/requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --no-cache-dir -r /tmp/requirements.txt

COPY code /workspace/code

ENV PATH=/opt/venv/bin:$PATH

ENTRYPOINT ["python", "/workspace/code/colabdesign_mpnn_af_demo.py"]
