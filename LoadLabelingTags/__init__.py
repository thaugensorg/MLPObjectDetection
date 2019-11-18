import logging
import requests
import json
import os
import azure.functions as func

# Note, as of 8/7/2019, the python client is not forming URLs correctly.  As a result this sample uses native HTTP calls to the training library.
# from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient

# https://2.python-requests.org//en/latest/api/
# https://stackoverflow.com/questions/9746303/how-do-i-send-a-post-request-as-a-json


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('ML Professoar HTTP trigger function LoadLabelingTags processed a request.')

    # Get Cognitive Services Environment Variables
    project_id = os.environ["ProjectID"]
    training_key = os.environ['TrainingKey']

    if project_id:
        labels_json = req.params.get('LabelsJson')
        if not labels_json:
            try:
                labels_json = req.form.get('LabelsJson')

            except Exception as e:
                message = str(e)
                return func.HttpResponse(
                    "Please pass JSON containing valid labels on the query string or in the request body using the parameter name: LabelsJson.  Error: " + message,
                    status_code=400
                )
        
        if labels_json:

            endpoint = os.environ['ClientEndpoint']

            # the consol app at this address shows how to properly form URLs for Cognitive Services custom model development https://westus2.dev.cognitive.microsoft.com/docs/services/fde264b7c0e94a529a0ad6d26550a761/operations/59568ae208fa5e09ecb9984e/console
            load_tags_url = endpoint + "/customvision/v3.0/Training/projects/" + project_id + "/tags"

            # set looping tracking variables
            count_of_labels_added = 0
            count_of_duplicate_labels = 0

            # code assumes json is in the form: {"Labels":["Hemlock","Japanese Cherry"]}
            label_dictionary = json.loads(labels_json)

            # loop through all labels passed into the function and add them to the project passed into the function
            for label in label_dictionary['Labels']:
                headers = {'Training-key': training_key}
                params = {'name': label}
                response = requests.post(endpoint, headers=headers,
                                        params=params)
                if "TagNameNotUnique" in response.text:
                    logging.info("Tag " + label + " is already in project and not unique, project id: " + project_id)
                    count_of_duplicate_labels = count_of_duplicate_labels + 1
                else:
                    count_of_labels_added = count_of_labels_added + 1
                
            return func.HttpResponse("Loaded " + str(count_of_labels_added) + " labels into project id: " + project_id + "  Note: " + str(count_of_duplicate_labels) + " labels were duplicates to existing project labels.  See log file for label names.")
    else:
        return func.HttpResponse(
             "Please configure ProjectID and/or TrainingKey in your environment variables.",
             status_code=400
        )
