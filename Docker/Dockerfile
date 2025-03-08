FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    libopencv-dev \
    tesseract-ocr \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install paddlepaddle-gpu -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html

COPY requirements.txt /app/requirements.txt

RUN python3 -m pip install -r /app/requirements.txt

CMD ["bash"]