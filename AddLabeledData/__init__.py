import logging
import time
import os
import requests
import json

import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry, Region

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('MLP Pbject Detection HTTP trigger function AddLabeledData processed a request.')

    image_url = req.params.get('ImageUrl')
    if not image_url:
        return func.HttpResponse(
                "Please pass a URL to an image to be added to training in this request on the query string.",
                status_code=400
        )

    image_labeling_json = req.params.get('LabeledRegions')
    if not image_labeling_json:
        try:
            image_labeling_json = req.get_json()
        except:
            return func.HttpResponse(
                "Please pass JSON containing the labeled regions associated with this image on the query string or in the request body.",
                status_code=400
            )

    labels = []
    labeled_images_with_regions = []
    count_of_regions_applied_to_image = 0
    count_of_lables_applied_to_region = 0

    endpoint = os.environ['ClientEndpoint']

    # Get Cognitive Services Environment Variables
    project_id = os.environ["ProjectID"]
    training_key = os.environ['TrainingKey']

    # load labeled image regions passed in request into dictionary
    image_labeling_json = '{ \
    "asset": { \
        "id": "8f10e29396fb15de2289535816503f14", \
        "format": "jpg", \
        "state": 2, \
        "type": 1, \
        "name": "failing_maple_1.jpg", \
        "path": "https://mlprofessoarstorage.blob.core.windows.net/pendingsupervision/failing_maple_1.jpg?sv=2018-03-28&ss=bfqt&srt=sco&sp=rwdlacup&se=2019-12-31T13:36:17Z&st=2019-09-27T04:36:17Z&spr=https&sig=0bFydcmEbb1Ejy1nMS518vP8KAkezam4B3G3XzKrDDI%3D", \
        "size": { \
            "width": 600, \
            "height": 600 \
        } \
    }, \
    "regions": [ \
        { \
            "id": "V3DFuPl1l", \
            "type": "RECTANGLE", \
            "tags": [ \
                "Maple" \
            ], \
            "boundingBox": { \
                "height": 555.0351288056206, \
                "width": 592.271662763466, \
                "left": 3.51288056206089, \
                "top": 4.918032786885246 \
            }, \
            "points": [ \
                { \
                    "x": 3.51288056206089, \
                    "y": 4.918032786885246 \
                }, \
                { \
                    "x": 595.7845433255269, \
                    "y": 4.918032786885246 \
                }, \
                { \
                    "x": 595.7845433255269, \
                    "y": 559.9531615925058 \
                }, \
                { \
                    "x": 3.51288056206089, \
                    "y": 559.9531615925058 \
                } \
            ] \
        } \
    ], \
    "version": "2.1.0" \
}'
    image_labeling_data = json.loads(image_labeling_json)

    # instanciate custom vision client
    trainer = CustomVisionTrainingClient(training_key, endpoint=endpoint)

    # get list of valid tags for this model
    tags = trainer.get_tags(project_id)

    # get the height and width of the image
    image_width = image_labeling_data['asset']['size']['width']
    image_height = image_labeling_data['asset']['size']['height']

    # for each labeled region in this asset get the map lables to tag ids and map boundaries formats
    # from vott to azure cognitive services then upload to the cognitive services project.
    for labeled_region in image_labeling_data['regions']:
        for label in labeled_region['tags']:
            for tag in tags:
                if tag.name == label:
                    labels.append(tag.id)
                    count_of_lables_applied_to_region = count_of_lables_applied_to_region + 1
                    break
        count_of_regions_applied_to_image = count_of_regions_applied_to_image + 1

        top_left_x = labeled_region['points'][0]['x']
        top_left_y = labeled_region['points'][0]['y']
        top_right_x = labeled_region['points'][1]['x']
        top_right_y = labeled_region['points'][1]['y']
        bottom_right_x = labeled_region['points'][2]['x']
        bottom_right_y = labeled_region['points'][2]['y']
        bottom_left_x = labeled_region['points'][3]['x']
        bottom_left_y = labeled_region['points'][3]['y']

        # calculate normalized coordinates.
        normalized_left = top_left_x / image_width
        normalized_top = top_left_y / image_height
        normalized_width = (top_right_x - top_left_x) / image_height
        normalized_height = (bottom_left_y - top_left_y) / image_height

        regions = [ Region(tag_id=labels[0], left=normalized_left,top=normalized_top,width=normalized_width,height=normalized_height) ]

    labeled_images_with_regions.append(ImageUrlCreateEntry(url=image_url, regions=regions))
    upload_result = trainer.create_images_from_urls(project_id, images=labeled_images_with_regions)

    if upload_result.is_batch_successful:
        return func.HttpResponse(
                "Image " + image_url + "successfully uploaded with " + count_of_regions_applied_to_image + " regions and " + count_of_lables_applied_to_region + " label(s) to project " + project_id,
                status_code=400
        )
    else:
        result = ""
        for image in upload_result.images:
            result = result + "Image status: " + image.status

        return func.HttpResponse(
                "Image batch upload failed with result: " + result,
                status_code=400
        )