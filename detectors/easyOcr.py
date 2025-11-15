
import easyocr
reader = easyocr.Reader(['en'],gpu=False)
result = reader.readtext('rotated_image.png')
texts = [(text, conf) for (_, text, conf) in result]

print(texts)
