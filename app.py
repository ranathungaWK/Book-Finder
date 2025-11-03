from flask import Flask, jsonify  ,request

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'error':'No image uploaded'}) , 400
    
    file = request.files['image']

    from PIL import Image
    import io

    try:
        img = Image.open(io.BytesIO(file.read()))
    except Exception as e:
        return jsonify({'error':f'cannot open image: {str(e)}'}) ,400

    return jsonify({'message':'Image uploaded successfully'})

if __name__ == '__main__':
    app.run(debug=True)