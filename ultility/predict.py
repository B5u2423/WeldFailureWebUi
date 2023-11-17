from ultralytics import YOLO
from PIL import Image
def yolo(weightPath,file,savePath):
    model = YOLO(weightPath)
    result = model(file)[0]
    im_base64 = Image.fromarray(result.plot()[..., ::-1])
    im_base64.save(savePath, format="JPEG")
