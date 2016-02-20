from googleapiclient import discovery
import base64
import requests
import json
from oauth2client.client import GoogleCredentials


class GCVWrapper:
    __base64_image = ''
    __key = ''

    def __init__(self, _filename, _key):
        with open(_filename, 'rb') as image_file:
            self.__base64_image = self.encode_image(image_file)
        self.__key = _key

    @staticmethod
    def get_batch_request(_content, _type):
        return json.dumps(
            {'requests': [{
                'image': {
                    'content': _content
                },
                'features': [{
                    'type': _type,
                    'maxResults': 1,
                }]
            }]}
        )

    @staticmethod
    def encode_image(image):
        """
        Pass the image data to an encoding function
        :param image:
         :return:
        """
        image_content = image.read()
        return base64.b64encode(image_content)

    def label_detection(self):
        batch_request = self.get_batch_request(self.__base64_image, 'LABEL_DETECTION')
        url = 'https://vision.googleapis.com/v1/images:annotate?key=%s' % self.__key
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, headers=headers, data=batch_request)
        return r.text

    def get_vision_service(self):
        discovery_url = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}?key=%s' % self.__key
        credentials = GoogleCredentials.get_application_default()
        return discovery.build('vision', 'v1', credentials=credentials,
                               discoveryServiceUrl=discovery_url)

    def face_detection(self):
        batch_request = self.get_batch_request(self.__base64_image, 'FACE_DETECTION')
        service = self.get_vision_service()
        request = service.images().annotate(body=batch_request)
        response = request.execute()
        return response['responses'][0]['faceAnnotations']


w = GCVWrapper('faulkner.jpg', 'AIzaSyDB2P8s2YMH3idk_vHsBRi2hdk4-DoGrGg')
# print w.label_detection()
print w.face_detection()
