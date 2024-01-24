import cv2
import numpy as np
from openvino.runtime import Core

ie = Core()
print(ie.available_devices)
model = ie.read_model(model="models/v3-small_224_1.0_float.xml")
compiled_model = ie.compile_model(model=model, device_name="MYRIAD")

output_layer = compiled_model.output(0)

# The MobileNet model expects images in RGB format.
image = cv2.cvtColor(cv2.imread(filename="images/coco.jpg"), code=cv2.COLOR_BGR2RGB)

# Resize to MobileNet image shape.
input_image = cv2.resize(src=image, dsize=(224, 224))

# Reshape to model input shape.
input_image = np.expand_dims(input_image, 0)
# cv2.imshow('input',image)
# cv2.waitKey(0)

result_infer = compiled_model([input_image])[output_layer]
result_index = np.argmax(result_infer)

# Convert the inference result to a class name.
imagenet_classes = open("labels/imagenet_2012.txt").read().splitlines()

# The model description states that for this model, class 0 is a background.
# Therefore, a background must be added at the beginning of imagenet_classes.
imagenet_classes = ['background'] + imagenet_classes

print(imagenet_classes[result_index])