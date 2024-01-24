FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y \
    software-properties-common \
    git \
    scons \
    build-essential

RUN git clone --recurse-submodules --single-branch --branch=releases/2022/3 https://github.com/openvinotoolkit/openvino.git
RUN git clone --recurse-submodules --single-branch --branch=releases/2022/3 https://github.com/openvinotoolkit/openvino_contrib.git

RUN DEBIAN_FRONTEND=noninteractive ./openvino/install_build_dependencies.sh
RUN apt install cython3

RUN add-apt-repository ppa:deadsnakes/ppa
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python3.9 python3.9-dev python3.9-distutils

RUN python3.9 -m pip install --upgrade pip
RUN python3.9 -m pip install -r /openvino/src/bindings/python/wheel/requirements-dev.txt

RUN mkdir build

WORKDIR /openvino/build
RUN cmake -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_PYTHON=ON \
    -DPYTHON_EXECUTABLE=`which python3.9` \
    -DPYTHON_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.9.so \
    -DPYTHON_INCLUDE_DIR=/usr/include/python3.9 \
    -DEANBLE_SYSTEM_PUGIXML=OFF \
    -DENABLE_WHEEL=ON \
    -DENABLE_INTEL_MYRIAD=ON \
    -DTHREADING=SEQ \
    -DCMAKE_CXX_FLAGS="-pthread" \
    -DIE_EXTRA_MODULES=/openvino_contrib/modules/arm_plugin \
    -DARM_COMPUTE_SCONS_JOBS=$(nproc --all) \..


RUN make --jobs=2
