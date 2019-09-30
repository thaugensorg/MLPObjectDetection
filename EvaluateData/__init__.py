import logging
import time
import os
import requests
import json

import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('MLP Pbject Detection HTTP trigger function AddLabeledData processed a request.')

    data_blob_url = req.params.get('DataBlobUrl')
    if not data_blob_url:
        return func.HttpResponse(
                "Please pass a URL to a blob containing the image to be added to training in this request on the query string.",
                status_code=400
        )

    labeled_regions_json = req.params.get('LabeledRegions')
    if not labeled_regions_json:
        try:
            labeled_regions_json = req.get_json()
        except:
            return func.HttpResponse(
                "Please pass JSON containing the labeled regions associated with this image on the query string or in the request body.",
                status_code=400
            )

    labels = []
    count_of_tags_applied_to_image = 0
    endpoint = os.environ['ClientEndpoint']

    # Get Cognitive Services Environment Variables
    project_id = os.environ["ProjectID"]
    training_key = os.environ['TrainingKey']

    # load labeled image regions passed in request into dictionary
    labeled_regions = json.loads(labeled_regions_json)

    # instanciate custom vision client
    trainer = CustomVisionTrainingClient(training_key, endpoint=endpoint)

    # get list of valid tags for this model
    tags = trainer.get_tags(project_id)
    for labeled_region in labeled_regions:
        for label in labeled_region:
            for tag in tags:
                if tag.name == label:
                    Labels.append(Tag.id)
                    CountOfTagsAppliedToTimage = CountOfTagsAppliedToTimage + 1
                    break



    if name:
        return func.HttpResponse(f"Hello {name}!")
    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )
