#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2018-2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
import argparse
import logging as log
import os
import sys
import time
import cv2
import numpy as np
try:
    from openvino.runtime import Core
    VERSION = 2022
except ImportError:
    from openvino.inference_engine import IECore as Core
    VERSION = 2021


def parse_args() -> argparse.Namespace:
    """Parse and return command line arguments"""
    parser = argparse.ArgumentParser(add_help=False)
    args = parser.add_argument_group('Options')
    # fmt: off
    args.add_argument('-h', '--help', action='help', help='Show this help message and exit.')
    args.add_argument('-m', '--model', default="models/ssdlite_mobilenet_v2.xml", type=str,
                      help='Required. Path to an .xml or .onnx file with a trained model.')
    args.add_argument('-i', '--input', default="images/coco.jpg", type=str, help='Required. Path to an image file.')
    args.add_argument('-l', '--extension', type=str, default=None,
                      help='Optional. Required by the CPU Plugin for executing the custom operation on a CPU. '
                      'Absolute path to a shared library with the kernels implementations.')
    args.add_argument('-c', '--config', type=str, default=None,
                      help='Optional. Required by GPU or VPU Plugins for the custom operation kernel. '
                      'Absolute path to operation description file (.xml).')
    args.add_argument('--labels', default="labels/coco.txt", type=str, help='Optional. Path to a labels mapping file.')
    # fmt: on
    return parser.parse_args()


def main(args, device):  # noqa
    log.basicConfig(format='[ %(levelname)s ] %(message)s', level=log.INFO, stream=sys.stdout)

    # ---------------------------Step 1. Initialize inference engine core--------------------------------------------------
    # log.info('Creating Inference Engine')
    ie = Core()

    # if args.extension and args.device == 'CPU':
    #     log.info(f'Loading the {args.device} extension: {args.extension}')
    #     ie.add_extension(args.extension, args.device)

    # if args.config and args.device in ('GPU', 'MYRIAD', 'HDDL'):
    #     log.info(f'Loading the {args.device} configuration: {args.config}')
    #     ie.set_config({'CONFIG_FILE': args.config}, args.device)

    # ---------------------------Step 2. Read a model in OpenVINO Intermediate Representation or ONNX format---------------
    # log.info(f'Reading the network: {args.model}')
    # (.xml and .bin files) or (.onnx file)
    net = ie.read_network(model=args.model)

    if len(net.input_info) != 1:
        log.error('The sample supports only single input topologies')
        return -1

    if len(net.outputs) != 1 and not ('boxes' in net.outputs or 'labels' in net.outputs):
        log.error('The sample supports models with 1 output or with 2 with the names "boxes" and "labels"')
        return -1

    # ---------------------------Step 3. Configure input & output----------------------------------------------------------
    # log.info('Configuring input and output blobs')
    # Get name of input blob
    input_blob = next(iter(net.input_info))

    # Set input and output precision manually
    net.input_info[input_blob].precision = 'U8'

    if len(net.outputs) == 1:
        output_blob = next(iter(net.outputs))
        net.outputs[output_blob].precision = 'FP16'
    else:
        net.outputs['boxes'].precision = 'FP16'
        net.outputs['labels'].precision = 'U16'

    # ---------------------------Step 4. Loading model to the device-------------------------------------------------------
    log.info(f'Loading the model to the plugin with device {device}')
    exec_net = ie.load_network(network=net, device_name=device)

    # ---------------------------Step 5. Create infer request--------------------------------------------------------------
    # load_network() method of the IECore class with a specified number of requests (default 1) returns an ExecutableNetwork
    # instance which stores infer requests. So you already created Infer requests in the previous step.

    # ---------------------------Step 6. Prepare input---------------------------------------------------------------------
    original_image = cv2.imread(args.input)
    image = original_image.copy()
    _, _, net_h, net_w = net.input_info[input_blob].input_data.shape

    if image.shape[:-1] != (net_h, net_w):
        log.warning(f'Image {args.input} is resized from {image.shape[:-1]} to {(net_h, net_w)}')
        image = cv2.resize(image, (net_w, net_h))

    # Change data layout from HWC to CHW
    image = image.transpose((2, 0, 1))
    # Add N dimension to transform to NCHW
    image = np.expand_dims(image, axis=0)

    # ---------------------------Step 7. Do inference----------------------------------------------------------------------
    log.info('Starting inference in synchronous mode')
    for i in range(5):
        res = exec_net.infer(inputs={input_blob: image})
    t1 = time.perf_counter()
    res = exec_net.infer(inputs={input_blob: image})
    t2 = time.perf_counter()
    log.info(f"Inference took {round(t2-t1,4)}s")

    # ---------------------------Step 8. Process output--------------------------------------------------------------------
    # Generate a label list
    if args.labels:
        with open(args.labels, 'r') as f:
            labels = [line.split(',')[0].strip() for line in f]

    output_image = original_image.copy()
    h, w, _ = output_image.shape

    if len(net.outputs) == 1:
        res = res[output_blob]
        # Change a shape of a numpy.ndarray with results ([1, 1, N, 7]) to get another one ([N, 7]),
        # where N is the number of detected bounding boxes
        detections = res.reshape(-1, 7)
    else:
        detections = res['boxes']
        labels = res['labels']
        # Redefine scale coefficients
        w, h = w / net_w, h / net_h

    for i, detection in enumerate(detections):
        if len(net.outputs) == 1:
            _, class_id, confidence, xmin, ymin, xmax, ymax = detection
        else:
            class_id = labels[i]
            xmin, ymin, xmax, ymax, confidence = detection

        if confidence > 0.5:
            label = labels[int(class_id)-1] if args.labels else int(class_id)

            xmin = int(xmin * w)
            ymin = int(ymin * h)
            xmax = int(xmax * w)
            ymax = int(ymax * h)

            log.info(f'Found: label = {label}, confidence = {confidence:.2f}, ' f'coords = ({xmin}, {ymin}), ({xmax}, {ymax})')

            # Draw a bounding box on a output image
            cv2.rectangle(output_image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(output_image, label, (xmin,ymin),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2,cv2.LINE_AA)

    # cv2.imwrite('out.jpg', output_image)
    # cv2.imshow('out',output_image)
    # cv2.waitKey(0)
    # if os.path.exists('out.bmp'):
    #     log.info('Image out.bmp created!')
    # else:
    #     log.error('Image out.bmp was not created. Check your permissions.')

    # ----------------------------------------------------------------------------------------------------------------------
    # log.info('This sample is an API example, for any performance measurements please use the dedicated benchmark_app tool\n')
    return 0


if __name__ == '__main__':
    args = parse_args()
    ie = Core()
    devices = ie.available_devices
    for device in devices:
        main(args,device)