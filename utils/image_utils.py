from PIL import Image
import io ,cv2
import numpy as np

def read_image(file):

    """Read image from uploaded file and convert to OpenCV format"""

    img = Image.open(io.BytesIO(file.read())).convert('RGB')
    img_cv = cv2.cvtColor(np.array(img),cv2.COLOR_RGB2BGR)
    return img_cv

def preprocess_image(img , target_size=(640,640), to_rgb=True, keep_aspect_ratio=True ):
    
    """Preprocess image for model input"""

    if keep_aspect_ratio:
        h , w = img.shape[:2]
        scale = min(target_size[0]/h , target_size[1]/w)
        new_w , new_h = int(w*scale) , int(h*scale)
        resized_img = cv2.resize(img, (new_w , new_h), interpolation=cv2.INTER_LINEAR)
        padded_img = np.full((target_size[0],target_size[1], 3), 0, dtype=np.uint8)
        padded_img[0:new_h , 0:new_w] = resized_img
    else:
        padded_img = cv2.resize(img, target_size, interpolation=cv2.INTER_LINEAR)
    
    if to_rgb:
        padded_img = cv2.cvtColor(padded_img , cv2.COLOR_BGR2RGB)
    

    return padded_img


def crop_image(img , detections)-> list :

    """Crop image using the given bounding box"""

    cropped_images = []
    for item in detections:
        x1 , y1 , x2 ,y2 = item['box']
        cropped = img[y1:y2 , x1:x2]
        cropped_images.append(cropped)
    

    return cropped_images