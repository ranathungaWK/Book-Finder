from flask import Flask, jsonify, request
from detectors import spine_detector
from utils.image_utils import read_image , preprocess_image , crop_image
from identifier.book_identifier import identify


app = Flask(__name__)

#initialize YOLO model
# device  = "cpu" 
# model = YOLO('models/best.pt').to(device)
# """ if you have a GPU, you can run this code 
#           model = YOLO('models/best.pt')
# """

#initialize easyocr reader
# reader = easyocr.Reader(['en'],gpu=False)

@app.route('/identifying_books',methods=['POST'])
def identify_books() -> dict:

    """Endpoint to detect spines in a uploaded image"""

    from ultralytics import YOLO
    import easyocr
    import cv2
    from PIL import Image
    import numpy as np
    
    # initialize YOLO and reader here
    model = YOLO('models/best.pt').to("cpu")
    reader = easyocr.Reader(['en'], gpu=False)
    device = "cpu"

    if 'image' not in request.files:
        return jsonify({'error':'No image uploaded'}) , 400
    
    file = request.files['image']
    img = read_image(file)

    model_img = preprocess_image(img , target_size=(640,640) , to_rgb=True , keep_aspect_ratio=True)

    results = spine_detector.spine_detector(model_img, model, confidence_threshold=0.5, device=device)

    crops = crop_image(model_img , results)
    outputs = []
    for cropped_array in crops:
        cropped_rgb = cv2.cvtColor(cropped_array, cv2.COLOR_RGB2BGR)
        pil_crop = Image.fromarray(cropped_rgb)
        rotated_crop_nparray = pil_crop.rotate(90, expand=True)

        if not isinstance(rotated_crop_nparray, np.ndarray):
            rotated_crop_nparray = np.array(rotated_crop_nparray)
        
        result = reader.readtext(rotated_crop_nparray)
        texts =[(text, conf) for (_, text, conf) in result]
        outputs.append(texts)

    if not results:
        return jsonify({'detections': []}), 200
    
    book_info = identify(ocr_predictions=outputs)
    
    return jsonify({'detections': outputs, 'book_info': book_info}), 200


if __name__ == '__main__':
    app.run(debug=True)