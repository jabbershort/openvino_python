#!/bin/bash

docker build -f 2022.Dockerfile -t ov .
docker run --name ov_container ov
docker cp ov_container:/openvino/build/wheels .
docker cp ov_container:/openvino/bin/intel64/Release/libopenvino_intel_myriad_plugin.so wheels/.
docker cp ov_container:/openvino/bin/intel64/Release/usb-ma2x8x.mvcmd wheels/.
