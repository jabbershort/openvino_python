FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y \
    git

RUN git clone --recurse-submodules --single-branch --branch=releases/2022/3 https://github.com/openvinotoolkit/openvino.git

WORKDIR /openvino

RUN DEBIAN_FRONTEND=noninteractive ./install_build_dependencies.sh
RUN apt-get install -y cython3 && \
    pip3 install --upgrade pip && \
    pip3 install -r src/bindings/python/wheel/requirements-dev.txt

RUN mkdir build

WORKDIR /openvino/build

RUN cmake -DCMAKE_BUILD_TYPE=Release -DENABLE_PYTHON=ON -DENABLE_SYSTEM_PUGIXML=ON -DENABLE_WHEEL=ON -DENABLE_INTEL_MYRIAD=ON ..
RUN make --jobs=$(nproc --all)
