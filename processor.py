import os
import io
# from io import BytesIO
from PIL import Image
import requests

from google.cloud import vision
# from google.cloud.vision_v1 import types

class Processor:
    # path = os.getcwd()
    # os.chdir(path)
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "Google_OCR_key.json"

    def __init__(self, itemID, url) -> str:
        self.itemID = itemID
        self.url = url

    def detect_text(self):
        # path = os.getcwd()
        # os.chdir(path)
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "Google_OCR_key.json"
        """Detects text in the file."""

        img = Image.open(requests.get(self.url, stream=True).raw)
        if self.itemID.endswith('_1') == False:
            img_width, img_height = img.size
            img_crop = img.crop((0, img_height//2, img_width,img_height))
        else:
            img_crop = img
        
        img_bytes = io.BytesIO()
        img_crop.save(img_bytes, format='jpeg')
        img_bytes = img_bytes.getvalue()
        
        client = vision.ImageAnnotatorClient()

        image = vision.Image(content = img_bytes)

        response = client.text_detection(image = image)
        texts = response.text_annotations
        text = texts[0].description
        text = text.strip()
        textList = text.split('\n')
        
        return textList

    def __str__(self) -> str:
        textList = self.detect_text()
        return 'OCR Result:{}'.format(textList)


'''test'''

'''
itemID = 's2621058'
url = 'https://cds.costcojapan.jp/cds/mail-images/upz/210418_42um/img18/s2621058.jpg'

Costco = Processor(itemID, url)
print(Costco.detect_text())

'''