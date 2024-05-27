import cv2
import numpy as np
import time
try:
    from openvino.runtime import Core
    VERSION = 2022
except ImportError:
    from openvino.inference_engine import IECore as Core
    VERSION = 2021

image_path = "images/elephant.jpg"

def run_test_2021(ie, device_name):
    model = ie.read_network(model="models/mobilenet-v3-small-1.0-224-tf.xml",weights="models/mobilenet-v3-small-1.0-224-tf.bin")
    compiled_model = ie.load_network(model, device_name=device_name, num_requests=1)
    input_key = next(iter(compiled_model.input_info))
    output_key = next(iter(compiled_model.outputs.keys()))

    # The MobileNet model expects images in RGB format.
    image = cv2.cvtColor(cv2.imread(filename=image_path), code=cv2.COLOR_BGR2RGB)

    # Resize to MobileNet image shape.
    input_image = cv2.resize(src=image, dsize=(224, 224))

    # Reshape to model input shape.
    input_image = np.expand_dims(input_image.transpose(2, 0, 1), 0)
    for i in range(5):
        result = compiled_model.infer(inputs={input_key: input_image})[output_key]
    t1 = time.perf_counter()
    result = compiled_model.infer(inputs={input_key: input_image})[output_key]
    t2 = time.perf_counter()
    result_index = np.argmax(result)
    # Convert the inference result to a class name.
    imagenet_classes = open("labels/imagenet_2012.txt").read().splitlines()

    # The model description states that for this model, class 0 is a background.
    # Therefore, a background must be added at the beginning of imagenet_classes.
    imagenet_classes = ['background'] + imagenet_classes

    print(imagenet_classes[result_index])
    print(f"Inference completed in {t2-t1}")

def run_test_2022(ie, device_name):
    model = ie.read_model(model="models/v3-small_224_1.0_float.xml")
    compiled_model = ie.compile_model(model=model, device_name=device_name)   

    output_layer = compiled_model.output(0)

    # The MobileNet model expects images in RGB format.
    image = cv2.cvtColor(cv2.imread(filename=image_path), code=cv2.COLOR_BGR2RGB)

    # Resize to MobileNet image shape.
    input_image = cv2.resize(src=image, dsize=(224, 224))

    # Reshape to model input shape.
    input_image = np.expand_dims(input_image,0)

    for i in range(5):
        result_infer = compiled_model([input_image])[output_layer]

    t1 = time.perf_counter()
    result_infer = compiled_model([input_image])[output_layer]
    t2 = time.perf_counter()
    result_index = np.argmax(result_infer)

    # Convert the inference result to a class name.
    imagenet_classes = open("labels/imagenet_2012.txt").read().splitlines()

    # The model description states that for this model, class 0 is a background.
    # Therefore, a background must be added at the beginning of imagenet_classes.
    imagenet_classes = ['background'] + imagenet_classes

    print(imagenet_classes[result_index])
    print(f"Inference completed in {t2-t1}")


if __name__ == "__main__":
    ie = Core()
    devices = ie.available_devices
    for device in devices:
        print(f'Running on {device}')
        if VERSION == 2021:
            run_test_2021(ie,device)
        else:
            run_test_2022(ie,device)



