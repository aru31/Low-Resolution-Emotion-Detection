"""
Step1: Preprocessing for Face Detection
"""

import os
import cv2
import numpy as np
import pandas as pd

from PIL import Image

from Constants.constants import FACE_SIZE


def read_csv(csv_data):
    """
    Pixel Values to be read from csv files for FERC-2013 dataset
    """
    data = pd.read_csv(csv_data)
    return data

def preprocess_image(image):
    """
    Code from OpenCV Docs for face Detcetion
    : Convert all images including RGB to GrayScale
    : Create Image with gray Region outside of the Image
    : Apply HaarImage Cascader on the image for face detection
    : If more than One Image, assumption that emotion
      label majorly from that face
    : Convert it back to face size as specified in paper using interpolation
    """
    if len(image.shape) > 2 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image = cv2.imdecode(image, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    gray_border = np.zeros((150, 150), np.uint8)
    gray_border[:, :] = 200
    gray_border[
        int((150/2) - (FACE_SIZE/2)): int((150/2) + (FACE_SIZE/2)),
        int((150/2) - (FACE_SIZE/2)): int((150/2) + (FACE_SIZE/2))
    ] = image
    image = gray_border
    path = 'HaarCascade/haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(path)
    faces = face_cascade.detectMultiScale(
        image,
        scaleFactor = 1.3,
        minNeighbors = 5
    )
    # The tuple is out of range i.e empty!
    # So, return None if necessary for no Image
    if not len(faces) > 0:
        return None

    max_area_face = faces[0]
    for face in faces:
        if face[2] * face[3] > max_area_face[2] * max_area_face[3]:
            max_area_face = face

    face = max_area_face
    image = image[face[1]:(face[1] + face[2]), face[0]:(face[0] + face[3])]
    try:
        image = cv2.resize(image, (FACE_SIZE, FACE_SIZE),
                           interpolation=cv2.INTER_CUBIC) / 255.
    except Exception:
        print("[+] Problem during resize")
        return None
    return image

def csv_to_numpy(data):
    """
    csv -> numpy array in form of image
    """
    pixel_list = np.array(data.split(" "))
    pixel_list = pixel_list.astype(np.uint8).reshape(FACE_SIZE, FACE_SIZE)
    pixel_list = Image.fromarray(pixel_list).convert('RGB')
    pixel_list = np.array(pixel_list)[:, :, ::-1].copy()
    pixel_list = preprocess_image(pixel_list)
    return pixel_list

# Script Using all the functions to create face detected images
def main():
    """
    : Main script to Run
    : Save images and labels as numpy object file
    """
    images = []
    labels = []
    path = 'Data/FER-2013/fer2013/fer2013.csv'
    total = read_csv(path).shape[0]
    for index, row in read_csv(path).iterrows():
        emotion = row['emotion']
        image = csv_to_numpy(row['pixels'])
        if image is not None:
            labels.append(emotion)
            images.append(image)
        index = index + 1

    np.save(os.path.join('Data', 'images.npy'), images)
    np.save(os.path.join('Data', 'labels.npy'), labels)

main()
