#!/bin/bash

docker build -t ov .
docker run --name ov_container ov
docker cp ov_container:/openvino/build/wheels .
docker cp ov_container:/openvino/bin/intel64/Release/libopenvino_intel_myriad_plugin.so wheels/.
