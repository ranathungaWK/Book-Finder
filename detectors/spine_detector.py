from ultralytics import YOLO


def spine_detector(image, model, confidence_threshold=0.5, device="cpu") -> list:

    """Detect spines of the given image using the provided model

    This function no longer imports `model` from `app` to avoid a circular
    import. The caller must pass the initialized model instance.
    """

    results = model.predict(source=image, conf=confidence_threshold, verbose=False)
    detections = []

    for r in results:
         
        for box, conf in zip(r.boxes.xyxy.cpu().numpy(), r.boxes.conf.cpu().numpy()):
            x1, y1, x2, y2 = box
            if conf >= confidence_threshold:
                detections.append({
                    "box": [int(x1), int(y1), int(x2), int(y2)],
                    "confidence": float(conf)
                })
                

    return detections