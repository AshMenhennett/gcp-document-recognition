import io 
import cv2
import numpy as np
from PIL import Image
from google.cloud import vision
from google.cloud.vision import types
from flask import Flask, request, jsonify

#Document Image Content Requirements
MINIMUM_REQUIRED_DOCUMENT_IMAGE_WIDTH=900
MINIMUM_REQUIRED_DOCUMENT_IMAGE_HEIGHT=400

gcp_client = vision.ImageAnnotatorClient()

app = Flask(__name__)

@app.route('/documentRecognitions', methods=['POST'])
def create_document_recognition():

    # Obtain Image
    request_image = request.files.get('image')
    request_image_binary = request_image.stream.read()

    # Create CV2 Image
    np_image_array = np.frombuffer(request_image_binary, np.uint8)
    cv2_image = cv2.imdecode(np_image_array, cv2.IMREAD_COLOR)

    # Obtain contours from CV2 Image
    greyscale_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)
    ret, binary_image = cv2.threshold(greyscale_image, 127, 255, cv2.THRESH_BINARY)
    im2, contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Find correct contour for document element of image
    cv2_document_image = None
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w >= MINIMUM_REQUIRED_DOCUMENT_IMAGE_WIDTH and h >= MINIMUM_REQUIRED_DOCUMENT_IMAGE_HEIGHT:
            cv2_document_image = cv2_image[y: y+h, x: x+w]
            break

    # Get bytes from the Image
    document_image = Image.fromarray(np.uint8(cv2_document_image)) 
    document_image_width, document_image_height = document_image.size
    document_image_bytes = io.BytesIO()
    document_image.save(document_image_bytes, format='PNG')
    document_image_bytes = document_image_bytes.getvalue()

    # Send bytes to GCP
    gcp_image = types.Image(content=document_image_bytes)
    gcp_response = gcp_client.text_detection(image=gcp_image)

    # Find Correct Text for given Templates
    api_response = []
    for annotation in gcp_response.text_annotations:
        result = find_data(annotation=annotation, 
            image_size=(document_image_width, document_image_height), 
                modes=['VIC_LICENCE_NUMBER', 'VIC_LICENCE_EXPIRY'])
        if result != None:
            api_response.append(result)

    return jsonify(api_response)

def is_bounded(mode, t, w, h, i):
    # The templates
    VIC_LICENCE_NUMBER = [(77.34, 21.27), (95.74, 21.27), (96.06, 27.63), (78.72,  27.13)]
    VIC_LICENCE_EXPIRY = [(1.48, 56.28), (27.12, 56.44), (27.12, 62.14), (1.48,  62.14)]

    list_to_use = locals()[mode]
    bounding = 5 # How many % can the templates be off?

    return diff(list_to_use[i][0],as_percentage(t[0], w)) <= bounding and diff(list_to_use[i][1], as_percentage(t[1], h)) <= bounding

def diff(a ,b):
    return a-b if a>=b else b-a

def as_percentage(a, b):
    return (a/b)*100

def find_data(annotation, image_size, modes):
    result = {}
    for mode in modes:
        iterate_and_find(annotation, image_size, mode, result)
    return result if result else None
    
def iterate_and_find(annotation, image_size, mode, result):
    idx = 0
    found_vertices = [False, False, False, False]
    for vSet in annotation.bounding_poly.vertices:
        if is_bounded(mode, (vSet.x, vSet.y), image_size[0], image_size[1], idx):
            found_vertices[idx] = True
            if False not in found_vertices:
                print('Found Text in Bounding Vertices: ' + annotation.description)
                result[mode] = annotation.description
            idx+=1
        else:
            break

app.run(debug=True)