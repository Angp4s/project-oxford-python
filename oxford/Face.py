import json
import requests

_detectUrl = 'https://api.projectoxford.ai/face/v0/detections';
_similarUrl = 'https://api.projectoxford.ai/face/v0/findsimilars';
_groupingUrl = 'https://api.projectoxford.ai/face/v0/groupings';
_identifyUrl = 'https://api.projectoxford.ai/face/v0/identifications';
_verifyUrl = 'https://api.projectoxford.ai/face/v0/verifications';
_personGroupUrl = 'https://api.projectoxford.ai/face/v0/persongroups';
_personUrl = 'https://api.projectoxford.ai/face/v0/persongroups';

class Face(object):
    """Client for using the Project Oxford face APIs"""
    
    def __init__(self, key):
        """Initializes a new instance of the class.
        Args:
            key (str). the API key to use for this client.
        """

        if key and isinstance(key, str):
            self.key = key
        else:
            raise Exception('Key is required but a string was not provided')
        
    def _return(self, response):
        if response.status_code is not 200:
            raise Exception(response.status_code + response.text)

        return response.json()

    def detect(self, options):
        """Detects human faces in an image and returns face locations, face landmarks, and
         optional attributes including head-pose, gender, and age. Detection is an essential
         API that provides faceId to other APIs like Identification, Verification,
         and Find Similar.

        Args:
            options (object). The Options object
            options.url (str). The URL to image to be used
            options.path (str). The Path to image to be used
            options.stream (stream). The Stream for image to be used
            options.analyzesFaceLandmarks (boolean). The Analyze face landmarks?
            options.analyzesAge (boolean). The Analyze age?
            options.analyzesGender (boolean). The Analyze gender?
            options.analyzesHeadPose (boolean). The Analyze headpose?

        Returns:
            object. The detection response 
        """

        # common header
        headers = {
            'Ocp-Apim-Subscription-Key': self.key
        }
    
        # build params query string
        params = {
            'analyzesFaceLandmarks': 'true' if 'analyzesFaceLandmarks' in options else 'false',
            'analyzesAge': 'true' if 'analyzesAge' in options else 'false',
            'analyzesGender': 'true' if 'analyzesGender' in options else 'false',
            'analyzesHeadPose': 'true' if 'analyzesHeadPose' in options else 'false'
        }

        # detect faces in a URL
        if 'url' in options and options['url'] != '':
            headers['Content-Type'] = 'application/json'
            result = requests.post(_detectUrl, json={'url': options['url']}, headers=headers, params=params)
        
        # detect faces from a local file
        elif 'path' in options and options['path'] != '':
            headers['Content-Type'] = 'application/octet-stream'
            result = requests.post(_detectUrl, data=open(options['path'], 'rb').read(), headers=headers, params=params)

        # detect faces in an octect stream
        elif 'stream' in options:
            headers['Content-Type'] = 'application/octet-stream'
            result = requests.post(_detectUrl, data=options['stream'], headers=headers, params=params)

        # fail if the options didn't specify an image source
        if result is None:
            raise Exception('either url, path, or stream must be specified')

        return self._return(result)

    def similar(self, sourceFace, candidateFaces):
        """Detect similar faces using faceIds (as returned from the detect API)

        Args:
            sourceFace (str). The source face
            candidateFaces (str[]). The source face

        Returns:
            object. The similarity response 
        """

        body = {
            'faceId': sourceFace,
            'faceIds': candidateFaces
        }
    
        result = requests.post(_similarUrl, json=body, headers={'Ocp-Apim-Subscription-Key': self.key})
        return self._return(result)

    def grouping(self, faceIds):
        """Divides candidate faces into groups based on face similarity using faceIds.
        The output is one or more disjointed face groups and a MessyGroup.
        A face group contains the faces that have similar looking, often of the same person.
        There will be one or more face groups ranked by group size, i.e. number of face.
        Faces belonging to the same person might be split into several groups in the result.
        The MessyGroup is a special face group that each face is not similar to any other
        faces in original candidate faces. The messyGroup will not appear in the result if
        all faces found their similar counterparts. The candidate face list has a
        limit of 100 faces.

        Args:
            faceIds (str[]). Array of faceIds to use

        Returns:
            object. The grouping response
        """

        body = { 'faceIds': faceIds }
    
        result = requests.post(_groupingUrl, json=body, headers={'Ocp-Apim-Subscription-Key': self.key})
        return self._return(result)

    def identify(self, faces, options):
        """Identifies persons from a person group by one or more input faces.
        To recognize which person a face belongs to, Face Identification needs a person group
        that contains number of persons. Each person contains one or more faces. After a person
        group prepared, it should be trained to make it ready for identification. Then the
        identification API compares the input face to those persons' faces in person group and
        returns the best-matched candidate persons, ranked by confidence.

        Args:
            faces (str[]). Array of faceIds to use
            options (object). The Options object
            options.personGroupId (str). The person group ID to use
            options.maxNumOfCandidatesReturned (str). Maximum number of candidates to return

        Returns:
            object. The identify response 
        """

        body = {
            'faceIds': faces
        }

        if options is not None:
            if options.personGroupId is not None:
                body['personGroupId'] = options.personGroupId
            if options.maxNumOfCandidatesReturned is not None:
                body['maxNumOfCandidatesReturned'] = options.maxNumOfCandidatesReturned

        result = requests.post(_identifyUrl, json=body, headers={'Ocp-Apim-Subscription-Key': self.key})
        return self._return(result)

    def verify(self, faceId1, faceId2):
        """Analyzes two faces and determine whether they are from the same person.
        Verification works well for frontal and near-frontal faces.
        For the scenarios that are sensitive to accuracy please use with own judgment.

        Args:
            faceId1 (str). The first face to compare
            faceId2 (str). The second face to compare
        
        Returns:
            object. The verify response 
        """

        body = {
            'faceId1': faceId1,
            'faceId2': faceId2
        }

        result = requests.post(_verifyUrl, json=body, headers={'Ocp-Apim-Subscription-Key': self.key})
        return self._return(result)