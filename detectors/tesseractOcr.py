import pytesseract
from PIL import Image 

MAX_WIDTH = 2000
MAX_HEIGHT = 2000
ALLOWED_FORMATS = ['PNG','JPEG']


def resize_image(image:Image.Image)->Image.Image:
    width , height = image.size
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        image.thumbnail((MAX_WIDTH,MAX_HEIGHT))
    return image


def text_from_image(image:Image.Image)->str:
    
    if not isinstance(image, Image.Image):
        raise TypeError("Input must be a PIL Image object")

    if image.format not in ALLOWED_FORMATS:
        raise ValueError(f"Unsupported image format: {image.format}")
    
    image  =resize_image(image)
        
    try:    
        text = pytesseract.image_to_string(image)
    except Exception as e:
        return "" 
    
    return " ".join(text.split())

# image2 = resize_image('detected_spines/spine_1.png')
image2 = Image.open('detected_spines/spine_5.png')

rotated_img = image2.rotate(90, expand=True)
rotated_img.save("rotated_image.png")
text2 = text_from_image(Image.open('rotated_image.png'))
print(text2)