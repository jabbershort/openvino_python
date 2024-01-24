FROM ubuntu:23.10

RUN apt-get update && \
    apt-get install -y \
    software-properties-common \
    git \
    cython3

RUN git clone --recurse-submodules --single-branch --branch=releases/2022/3 https://github.com/openvinotoolkit/openvino.git

RUN DEBIAN_FRONTEND=noninteractive ./openvino/install_build_dependencies.sh
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r /openvino/src/bindings/python/wheel/requirements-dev.txt

RUN mkdir build

WORKDIR /openvino/build
RUN cmake -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_PYTHON=ON \
    -DPYTHON_EXECUTABLE=`which python3.11` \
    -DPYTHON_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.11.so \
    -DPYTHON_INCLUDE_DIR=/usr/include/python3.11 \
    -DEANBLE_SYSTEM_PUGIXML=OFF \
    -DENABLE_WHEEL=ON \
    -DENABLE_INTEL_MYRIAD=ON ..

RUN make --jobs=$(nproc --all)
