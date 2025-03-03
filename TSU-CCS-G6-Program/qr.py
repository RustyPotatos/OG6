import cv2
import numpy as np
from pyzbar.pyzbar import decode

def scan_qr_code():
    cap = cv2.VideoCapture(0)  # Open webcam

    while True:
        ret, frame = cap.read()  # Capture frame-by-frame
        if not ret:
            break

        for qr_code in decode(frame):
            qr_data = qr_code.data.decode('utf-8')
            print(f"QR Code Data: {qr_data}")

            # Draw a rectangle around the QR code
            points = qr_code.polygon
            if len(points) == 4:
                pts = [(p.x, p.y) for p in points]
                cv2.polylines(frame, [np.array(pts, np.int32)], True, (0, 255, 0), 3)

        cv2.imshow("QR Code Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

scan_qr_code()
