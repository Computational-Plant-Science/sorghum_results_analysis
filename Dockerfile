#Name: Dockerfile
#Version: 1.0
#Summary: 
#Author: Brian Nguyen
#Author-email: bhn@arizona.edu
#Created: 2025-05-08

FROM --platform=linux/amd64 ubuntu:20.04

LABEL maintainer='Brian Nguyen'
LABEL version="1.0"
LABEL description="Docker image for trait analysis and visualization pipeline"

COPY ./ /opt/code
WORKDIR /opt/code

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt update && apt install -y \
    tzdata \
    build-essential \
    python3 \
    python3-pip \
    python3-setuptools \
    software-properties-common \
    libxext6 \
    libsm6 \
    libxrender-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxcursor-dev \
    libxi-dev \
    libboost-all-dev \
    cmake-gui \
    xorg-dev \
    nano \
    git \
 && apt clean && rm -rf /var/lib/apt/lists/*


 RUN pip3 install --upgrade pip && pip3 install \
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

RUN chmod +x /opt/code/*.py || true
RUN chmod +x /opt/code/*.sh || true

ENV PYTHONPATH=/opt/code:$PYTHONPATH
ENV LD_LIBRARY_PATH=/opt/code:$LD_LIBRARY_PATH





# docker build --platform linux/amd64 -t trait-pipeline -f Dockerfile .
# docker run -v $(pwd)/data:/srv/data -it trait-pipeline bash