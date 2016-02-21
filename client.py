# -*- coding: utf-8 -*-
import argparse
import base64
import logging
import httplib2
from apiclient.discovery import build
from PIL import Image, ImageDraw


class GoogleCloudVisionClient:
    __base64_image = ''
    __url = 'https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'
    __service = None
    __max_results = 1
    __filename = ''

    def __init__(self, _filename, _key, _max_results):
        with open(_filename, 'rb') as image_file:
            self.__base64_image = self.encode_image(image_file)
        self.__service = build('vision', 'v1', httplib2.Http(), discoveryServiceUrl=self.__url, developerKey=_key)
        self.__max_results = _max_results
        self.__filename = _filename

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

    def make_detection(self, _type):
        batch_request = self.get_batch_request(self.__base64_image, _type)
        request = self.__service.images().annotate(body=batch_request)
        response = request.execute()
        return response

    def highlight_faces(self, faces, output_filename):
        """Draws a polygon around the faces, then saves to output_filename.

        Args:
          faces: a list of faces found in the file. This should be in the format
              returned by the Vision API.
          output_filename: the name of the image file to be created, where the faces
              have polygons drawn around them.
        """
        im = Image.open(self.__filename)
        draw = ImageDraw.Draw(im)

        for face in faces:
            box = [(v['x'], v['y']) for v in face['fdBoundingPoly']['vertices']]
            draw.line(box + [box[0]], width=5, fill='#00ff00')

        del draw
        im.save(output_filename)


if __name__ == '__main__':
    logging.basicConfig(filename='debug.log', level=logging.DEBUG)
    p = argparse.ArgumentParser()
    p.add_argument("-k", dest='api_key', help='API key', required=True)
    p.add_argument('-i', dest='image_file', help='The image you\'d like to label.', default='image.jpg')
    p.add_argument('--max-results', default=1)
    args = p.parse_args()
    w = GoogleCloudVisionClient(args.image_file, args.api_key, args.max_results)

    face_detection = True if raw_input('FACE_DETECTION? (y/n) ') in ['y', 'Y'] else False
    logo_detection = True if raw_input('LOGO_DETECTION? (y/n) ') in ['y', 'Y'] else False
    text_detection = True if raw_input('TEXT_DETECTION? (y/n) ') in ['y', 'Y'] else False
    label_detection = True if raw_input('LABEL_DETECTION? (y/n) ') in ['y', 'Y'] else False

    if face_detection:
        res = w.make_detection('FACE_DETECTION')
        if res['responses'][0]:
            w.highlight_faces(res['responses'][0]['faceAnnotations'], 'out.jpg')
            print('Detected face: %s' % res['responses'][0]['faceAnnotations'])
        else:
            print 'Faces not detected'

    if logo_detection:
        res = w.make_detection('LOGO_DETECTION')
        if res['responses'][0]:
            logos = ', '.join([r['description'].strip() for r in res['responses'][0]['logoAnnotations']])
            print('Detected logos: %s' % logos)
        else:
            print 'Logos not detected'

    if text_detection:
        res = w.make_detection('TEXT_DETECTION')
        if res['responses'][0]:
            texts = ', '.join([r['description'].strip() for r in res['responses'][0]['textAnnotations']])
            print('Detected texts: %s' % texts)
        else:
            print 'Texts not detected'

    if label_detection:
        res = w.make_detection('LABEL_DETECTION')
        if res['responses'][0]:
            labels = ', '.join([r['description'].strip() for r in res['responses'][0]['labelAnnotations']]).strip()
            print('Found labels: %s' % labels)
        else:
            print 'Labels not detected'
