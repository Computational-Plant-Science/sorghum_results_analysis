#Name: Dockerfile
#Version: 1.0
#Summary: 
#Author: Brian Nguyen
#Author-email: bhn@arizona.edu
#Created: 2025-05-08

FROM --platform=linux/amd64 python:3.11-slim

LABEL maintainer='Brian Nguyen'
LABEL version="1.0"
LABEL description="Docker image for trait analysis and visualization pipeline"

ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC

RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/code


RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        numpy \
        pandas \
        matplotlib \
        seaborn \
        plotly \
        openpyxl \
        opencv-python-headless \
        pathlib \
        pyyaml \
        imutils \
        rembg \
        pytest

COPY . .
RUN chmod +x pipeline.sh *.py

ENTRYPOINT ["python3"]

