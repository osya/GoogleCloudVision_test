# Import the base64 encoding library
import base64
import requests
import json


# Pass the image data to an encoding function
def encode_image(image):
    image_content = image.read()
    return base64.b64encode(image_content)


with open('faulkner.jpg', 'rb') as image_file:
    encoded_string = encode_image(image_file)

url = 'https://vision.googleapis.com/v1/images:annotate?key=%s' % 'AIzaSyDB2P8s2YMH3idk_vHsBRi2hdk4-DoGrGg'
headers = {'Content-type': 'application/json'}
data = json.dumps({
  'requests': [
    {
      'image': {
        'content': encoded_string
      },
      'features': [
        {
          'type': 'LABEL_DETECTION',
          'maxResults': 1
        }
      ]
    }
  ]
})
r = requests.post(url, headers=headers, data=data)
print r.text
