import argparse
import base64
import logging
import httplib2
from apiclient.discovery import build


class GCVWrapper:
    __base64_image = ''
    __url = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'
    __service = None
    __max_results = 1

    def __init__(self, _filename, _key, _max_results):
        with open(_filename, 'rb') as image_file:
            self.__base64_image = self.encode_image(image_file)
        self.__service = build('vision', 'v1', httplib2.Http(), discoveryServiceUrl=self.__url, developerKey=_key)
        self.__max_results = _max_results

    def get_batch_request(self, _content, _type):
        return {'requests': [{
            'image': {'content': _content},
            'features': [{'type': _type, 'maxResults': self.__max_results}]
        }]}

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
        request = self.__service.images().annotate(body=batch_request)
        response = request.execute()
        return response

    def face_detection(self):
        batch_request = self.get_batch_request(self.__base64_image, 'FACE_DETECTION')
        request = self.__service.images().annotate(body=batch_request)
        response = request.execute()
        return response['responses'][0]['faceAnnotations']


if __name__ == '__main__':
    logging.basicConfig(filename='debug.log', level=logging.DEBUG)
    p = argparse.ArgumentParser()
    p.add_argument("-k", dest='api_key', help='API key', required=True)
    p.add_argument('-i', dest="image_path", help='path to image', required=True)
    p.add_argument('--max-results', default=1)
    args = p.parse_args()
    w = GCVWrapper(args.i if args.i else 'image.jpg', args.api_key, args.max_results)
    res = w.label_detection()
    # res = w.face_detection()
    print res
