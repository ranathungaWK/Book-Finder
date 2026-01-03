# 📚 Book Finder

An intelligent computer vision application that identifies books from shelf images using YOLOv8 object detection and OCR technology. Simply upload an image of your bookshelf, and the system will automatically detect book spines, extract text, and identify the books.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **🔍 Automated Book Detection**: Uses YOLOv8 deep learning model to detect book spines in images
- **📖 OCR Text Extraction**: Extracts text from book spines using EasyOCR
- **🎯 High Accuracy**: Fine-tuned YOLO model specifically trained for book spine detection
- **👤 User Authentication**: Secure user registration and login system
- **📊 Reading History**: Track books you've read with timestamps
- **🖼️ Image Processing**: Intelligent image preprocessing for optimal detection
- **🌐 REST API**: RESTful endpoints for easy integration

## 🚀 Tech Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database management
- **YOLOv8** (Ultralytics) - Object detection
- **EasyOCR** - Optical character recognition
- **PyTorch** - Deep learning framework
- **OpenCV** - Image processing
- **Pillow** - Image manipulation

### Machine Learning
- **Custom YOLO Model** - Fine-tuned for book spine detection
- **Sentence Transformers** - Text embeddings (optional)
- **scikit-learn** - Machine learning utilities

### Database
- **SQLAlchemy ORM** - Database abstraction
- **Alembic** - Database migrations

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) CUDA-capable GPU for faster inference
- Virtual environment (recommended)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Book-Finder.git
   cd Book-Finder
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///bookfinder.db
   ```

5. **Initialize the database**
   ```bash
   flask db upgrade
   ```

6. **Download the trained model**
   - Place your trained `best.pt` model in the `models/` directory
   - Or train your own model using the data in `finetune/`

## 🎮 Usage

### Starting the Application

```bash
python app.py
```

The server will start at `http://localhost:5000`

### API Endpoints

#### 1. **Book Identification**
```http
POST /books/identifying_books
Content-Type: multipart/form-data

Body:
- image: [image file]
```

**Response:**
```json
{
  "detections": [
    {
      "box": [x1, y1, x2, y2],
      "confidence": 0.95,
      "text": "Book Title",
      "author": "Author Name"
    }
  ]
}
```

#### 2. **User Authentication**
```http
POST /auth/register
POST /auth/login
```

### Example Usage with Python

```python
import requests

# Upload an image for book detection
url = "http://localhost:5000/books/identifying_books"
files = {'image': open('bookshelf.jpg', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

### Example Usage with curl

```bash
curl -X POST -F "image=@bookshelf.jpg" http://localhost:5000/books/identifying_books
```

## 📁 Project Structure

```
Book-Finder/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── database/                   # Database models and setup
│   ├── models.py              # SQLAlchemy models
│   └── db_setup.py            # Database configuration
├── detectors/                  # Detection modules
│   ├── spine_detector.py      # YOLO-based spine detection
│   ├── easyOcr.py            # EasyOCR integration
│   └── tesseractOcr.py       # Tesseract OCR alternative
├── identifier/                 # Book identification logic
│   └── book_identifier.py     # Book matching and identification
├── routes/                     # Flask blueprints
│   ├── auth_routes.py         # Authentication endpoints
│   └── book_identifier_route.py  # Book detection endpoints
├── services/                   # Business logic
│   ├── book_service.py        # Book-related services
│   └── user_service.py        # User management
├── utils/                      # Utility functions
│   ├── image_utils.py         # Image processing utilities
│   └── validators.py          # Input validation
├── models/                     # Trained ML models
│   └── best.pt               # Fine-tuned YOLOv8 model
├── finetune/                   # Training data and scripts
│   ├── data.yaml             # Dataset configuration
│   └── train/valid/test/     # Dataset splits
└── frontend/                   # Frontend files
    └── new.html              # Web interface
```

## 🎯 How It Works

1. **Image Upload**: User uploads an image of a bookshelf
2. **Preprocessing**: Image is resized and normalized to 640x640
3. **Spine Detection**: YOLOv8 model detects book spine locations
4. **Image Cropping**: Detected regions are cropped from the original image
5. **Text Extraction**: EasyOCR extracts text from each cropped spine
6. **Book Identification**: Extracted text is processed to identify book titles and authors
7. **Response**: JSON response with detected books and their locations

## 🔧 Configuration

### Model Settings
Edit detection parameters in [routes/book_identifier_route.py](routes/book_identifier_route.py):
```python
confidence_threshold = 0.5  # Adjust detection confidence
device = "cpu"              # Use "cuda" for GPU acceleration
```

### OCR Settings
Configure OCR languages in the route:
```python
reader = easyocr.Reader(['en'], gpu=False)  # Add more languages if needed
```

## 🏋️ Training Your Own Model

1. Prepare your dataset in YOLO format
2. Update [finetune/data.yaml](finetune/data.yaml) with your dataset paths
3. Run training:
   ```python
   from ultralytics import YOLO
   
   model = YOLO('yolo11n.pt')
   model.train(data='finetune/data.yaml', epochs=100, imgsz=640)
   ```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AllEyesOnMe`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AllEyesOnMe`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- OCR accuracy depends on image quality and lighting
- Performance may be slower on CPU compared to GPU
- Currently supports English text only (can be extended to other languages)

## 🚧 Future Enhancements

- [ ] Add support for multiple languages
- [ ] Integrate with book databases (Google Books API, OpenLibrary)
- [ ] Mobile application
- [ ] Real-time video detection
- [ ] Book recommendation system based on detected books
- [ ] Export reading list functionality
- [ ] Barcode/ISBN scanning

## 📞 Contact

For questions or support, please open an issue on GitHub.

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) for the object detection framework
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) for optical character recognition
- [Flask](https://flask.palletsprojects.com/) for the web framework

---

⭐ If you find this project useful, please consider giving it a star! 
