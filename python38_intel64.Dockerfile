FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y \
    git

RUN git clone --recurse-submodules --single-branch --branch=releases/2022/3 https://github.com/openvinotoolkit/openvino.git

RUN DEBIAN_FRONTEND=noninteractive ./openvino/install_build_dependencies.sh
RUN apt install cython3

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r /openvino/src/bindings/python/wheel/requirements-dev.txt

RUN mkdir build

WORKDIR /openvino/build
RUN cmake -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_PYTHON=ON \
    -DEANBLE_SYSTEM_PUGIXML=OFF \
    -DENABLE_WHEEL=ON \
    -DENABLE_INTEL_MYRIAD=ON ..

RUN make --jobs=$(nproc --all)
