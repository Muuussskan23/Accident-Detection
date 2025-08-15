!pip install twilio
import cv2
import numpy as np
from PIL import Image as PILImage
from IPython.display import display, Javascript, Audio
from google.colab.output import eval_js
from base64 import b64decode
import wave
import time
from twilio.rest import Client

!pip install opencv-python-headless twilio

!wget https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg -O yolov4.cfg
!wget https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4.weights -O yolov4.weights
!wget https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names -O coco.names

net = cv2.dnn.readNet("yolov4.weights", "yolov4.cfg")

with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

vehicle_classes = {"car", "bus", "truck", "motorcycle","bicycle"}
person_classes = {"person"}
target_classes = vehicle_classes | person_classes

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]

def capture_image(filename='photo.jpg', quality=0.8):
    js = Javascript('''
        async function captureImage(quality) {
            const video = document.createElement('video');
            const stream = await navigator.mediaDevices.getUserMedia({video: true});
            document.body.appendChild(video);
            video.srcObject = stream;
            await video.play();

            await new Promise(resolve => setTimeout(resolve, 1000));

            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);

            const dataUrl = canvas.toDataURL('image/jpeg', quality);
            stream.getVideoTracks()[0].stop();
            video.remove();
            canvas.remove();

            return dataUrl;
        }
    ''')

    display(js)
    data_url = eval_js('captureImage({})'.format(quality))
    binary = b64decode(data_url.split(',')[1])
    with open(filename, 'wb') as f:
        f.write(binary)
    return filename

def detect_objects(image):
    height, width, channels = image.shape

    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids, confidences, boxes = [], [], []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            # Ensure the class_id is valid and check if it's a vehicle or person
            if confidence > 0.5 and 0 <= class_id < len(classes) and classes[class_id] in target_classes:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = confidences[i]
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, f"{label}: {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return image, boxes, class_ids

def detect_accidents(boxes, class_ids):
    accident_detected = False
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            box1 = boxes[i]
            box2 = boxes[j]
            label1 = classes[class_ids[i]]
            label2 = classes[class_ids[j]]

            if (label1 in vehicle_classes and label2 in person_classes) or (label1 in person_classes and label2 in vehicle_classes):
                if (box1[0] < box2[0] + box2[2] and box1[0] + box1[2] > box2[0] and
                    box1[1] < box2[1] + box2[3] and box1[1] + box1[3] > box2[1]):
                    print(f"ALERT: Potential accident detected ")
                    accident_detected = True
                    break
        if accident_detected:
            break
    if not accident_detected:
      print("No accident detected")
    return accident_detected

def play_alarm():
    frequency = 3000
    fs = 44100
    duration = 3

    t = np.linspace(0, duration, int(fs * duration), endpoint=False)

    note = np.sin(2 * np.pi * frequency * t)

    audio = np.int16(note / np.max(np.abs(note)) * 32767)

    with wave.open('alarm.wav', 'w') as wf:
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(fs)
        wf.writeframes(audio.tobytes())

    display(Audio('alarm.wav', autoplay=True))

def make_phone_call():
    account_sid = '#replace with your twilio account_sid'
    auth_token = '#replace with your twilio auth_token'
    client = Client(account_sid, auth_token)

    twilio_number = '#replace with your twilio number'

    to_number = '#replace with the phone number on which you want to receive a call.'
    call = client.calls.create(
        twiml='<Response><Say>An accident has been detected. Please respond accordingly.</Say></Response>',
        to=to_number,
        from_=twilio_number
    )

    print(f"Call initiated, SID: {call.sid}")

def live_feed():
    try:
        while True:
            filename = capture_image()
            print(f"Captured Image: {filename}")

            image = cv2.imread(filename)

            if image is None:
                print("Error: Image not loaded correctly.")
                continue

            result_image, boxes, class_ids = detect_objects(image)

            accident_detected = detect_accidents(boxes, class_ids)

            result_pil_image = PILImage.fromarray(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
            display(result_pil_image)

            if accident_detected:
                play_alarm()
                make_phone_call()
            else:
                print("No accident detected")

            time.sleep(2)
    except KeyboardInterrupt:
        print("Live feed stopped by user.")

live_feed()