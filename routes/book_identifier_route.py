from flask import Blueprint, jsonify, request
from detectors import spine_detector
from utils.image_utils import read_image , preprocess_image , crop_image
from identifier.book_identifier import identify
import os
from werkzeug.utils import secure_filename
from datetime import datetime

book_identifier_bp = Blueprint("book_identifier" , __name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'mp3', 'wav', 'ogg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_attached_file(file):
    """Save attached file and return file info"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid filename conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        return {
            'filename': file.filename,
            'saved_filename': filename,
            'filepath': filepath,
            'file_size': os.path.getsize(filepath),
            'file_type': filename.rsplit('.', 1)[1].lower()
        }
    return None

@book_identifier_bp.route('/identifying_books',methods=['POST'])
def identify_books() -> dict:

    """Endpoint to detect spines in a uploaded image with optional file attachments"""

    try:
        from ultralytics import YOLO
        import easyocr
        import cv2
        from PIL import Image
        import numpy as np
        import traceback
    except ImportError as e:
        return jsonify({
            'error': 'Required library not installed',
            'message': str(e),
            'details': 'Please install required dependencies: ultralytics, easyocr, opencv-python, pillow, numpy'
        }), 500

    try:
        # Check for main image
        if 'image' not in request.files:
            return jsonify({'error':'No image uploaded', 'message': 'Please upload an image file'}) , 400
        
        file = request.files['image']
        
        # Validate main image file
        if file.filename == '':
            return jsonify({'error':'No image file selected', 'message': 'Please select a valid image file'}) , 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error':'Invalid image file type',
                'message': f'Allowed file types: png, jpg, jpeg, gif. Received: {file.filename.rsplit(".", 1)[-1] if "." in file.filename else "unknown"}'
            }) , 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'error':'File size too large',
                'message': f'File size ({file_size / (1024*1024):.2f}MB) exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB'
            }) , 400
        
        # Process main image
        try:
            img = read_image(file)
        except Exception as e:
            return jsonify({
                'error': 'Failed to read image',
                'message': str(e)
            }), 400

        try:
            model_img = preprocess_image(img , target_size=(640,640) , to_rgb=True , keep_aspect_ratio=True)
        except Exception as e:
            return jsonify({
                'error': 'Failed to preprocess image',
                'message': str(e)
            }), 500

        try:
            # Initialize YOLO model
            model = YOLO('models/best.pt').to("cpu")
            results = spine_detector.spine_detector(model_img, model, confidence_threshold=0.5, device="cpu")
        except FileNotFoundError:
            return jsonify({
                'error': 'Model file not found',
                'message': 'YOLO model file (models/best.pt) not found. Please ensure the model file exists.'
            }), 500
        except Exception as e:
            return jsonify({
                'error': 'Failed to detect book spines',
                'message': str(e)
            }), 500

        try:
            crops = crop_image(model_img , results)
            outputs = []
            
            # Initialize EasyOCR reader
            reader = easyocr.Reader(['en'], gpu=False)
            
            for cropped_array in crops:
                try:
                    cropped_rgb = cv2.cvtColor(cropped_array, cv2.COLOR_RGB2BGR)
                    pil_crop = Image.fromarray(cropped_rgb)
                    rotated_crop_nparray = pil_crop.rotate(90, expand=True)

                    if not isinstance(rotated_crop_nparray, np.ndarray):
                        rotated_crop_nparray = np.array(rotated_crop_nparray)
                    
                    result = reader.readtext(rotated_crop_nparray)
                    texts =[(text, conf) for (_, text, conf) in result]
                    outputs.append(texts)
                except Exception as e:
                    print(f"Error processing crop: {e}")
                    continue
        except Exception as e:
            return jsonify({
                'error': 'Failed to process OCR',
                'message': str(e)
            }), 500

        # Process attached files
        attached_files_info = []
        try:
            if 'attached_files' in request.files:
                attached_files = request.files.getlist('attached_files')
                for attached_file in attached_files:
                    if attached_file.filename != '':  # Check if file was actually uploaded
                        file_info = save_attached_file(attached_file)
                        if file_info:
                            attached_files_info.append({
                                'original_filename': file_info['filename'],
                                'saved_filename': file_info['saved_filename'],
                                'file_size': file_info['file_size'],
                                'file_type': file_info['file_type'],
                                'uploaded_at': datetime.now().isoformat()
                            })
            
            # Also check for 'files' key (alternative naming)
            if 'files' in request.files:
                attached_files = request.files.getlist('files')
                for attached_file in attached_files:
                    if attached_file.filename != '':
                        file_info = save_attached_file(attached_file)
                        if file_info:
                            attached_files_info.append({
                                'original_filename': file_info['filename'],
                                'saved_filename': file_info['saved_filename'],
                                'file_size': file_info['file_size'],
                                'file_type': file_info['file_type'],
                                'uploaded_at': datetime.now().isoformat()
                            })
        except Exception as e:
            print(f"Error processing attached files: {e}")
            # Continue even if attached files fail

        if not results:
            return jsonify({
                'detections': [],
                'attached_files': attached_files_info,
                'message': 'No book spines detected in the image',
                'success': True
            }), 200
        
        try:
            book_info = identify(ocr_predictions=outputs)
        except Exception as e:
            print(f"Error identifying books: {e}")
            book_info = {
                'error': 'Failed to identify books',
                'message': str(e)
            }
        
        return jsonify({
            'detections': outputs, 
            'book_info': book_info,
            'attached_files': attached_files_info,
            'attached_files_count': len(attached_files_info),
            'success': True
        }), 200
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Unexpected error in identify_books: {error_trace}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'traceback': error_trace
        }), 500
