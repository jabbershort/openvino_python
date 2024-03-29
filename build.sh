
#!/bin/bash

mkdir build || echo "build folder exists"

arch=$(uname -i)

if [[ $arch == x86_64* ]]; then
    SUBFOLDER="intel64"
else
    SUBFOLDER="aarch64"
fi

docker build -f python38_$SUBFOLDER.Dockerfile -t ov38 .
docker run --name ov-38 ov38
mkdir build/py38
docker cp ov-38:/openvino/build/wheels build/py38/.
docker cp ov-38:/openvino/bin/$SUBFOLDER/Release/libopenvino_intel_myriad_plugin.so build/py38/wheels/.
docker cp ov-38:/openvino/bin/$SUBFOLDER/Release/usb-ma2x8x.mvcmd build/py38/wheels/.
docker rm ov-38

docker build -f python39_$SUBFOLDERDockerfile -t ov39 .
docker rm ov-39
docker run --name ov-39 ov39
mkdir build/py39 || echo "build folder exists"
docker cp ov-39:/openvino/build/wheels build/py39/.
docker cp ov-39:/openvino/bin/$SUBFOLDER/Release/libopenvino_intel_myriad_plugin.so build/py39/wheels/.
docker cp ov-39:/openvino/bin/$SUBFOLDER/Release/usb-ma2x8x.mvcmd build/py39/wheels/.
docker rm ov-39

docker build -f python310_$SUBFOLDER.Dockerfile -t ov310 .
docker rm ov-310
docker run --name ov-310 ov310
mkdir build/py310|| echo "build folder exists"
docker cp ov-310:/openvino/build/wheels build/py310/.
docker cp ov-310:/openvino/bin/$SUBFOLDER/Release/libopenvino_intel_myriad_plugin.so build/py310/wheels/.
docker cp ov-310:/openvino/bin/$SUBFOLDER/Release/usb-ma2x8x.mvcmd build/py310/wheels/.
docker rm ov-310

docker build -f python311_$SUBFOLDER.Dockerfile -t ov311 .
docker rm ov-311
docker run --name ov-311 ov311
mkdir build/py311 || echo "build folder exists"
docker cp ov-311:/openvino/build/wheels build/py311/.
docker cp ov-311:/openvino/bin/$SUBFOLDER/Release/libopenvino_intel_myriad_plugin.so build/py311/wheels/.
docker cp ov-311:/openvino/bin/$SUBFOLDER/Release/usb-ma2x8x.mvcmd build/py311/wheels/.
docker rm ov-311 
