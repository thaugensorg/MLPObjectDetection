import logging
import os
import json
import requests

import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    data_url = req.params.get('ImageUrl')
    if not data_url:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            data_url = req_body.get('ImageUrl')

    if data_url:

        # Get Cognitive Services Environment Variables
        project_id = os.environ["ProjectID"]
        training_key = os.environ['TrainingKey']
        prediction_key = os.environ['PredictionKey']
        client_endpoint = os.environ['ClientEndpoint']


        trainer = CustomVisionTrainingClient(training_key, endpoint=client_endpoint)
        iterations = trainer.get_iterations(project_id)
        if len(iterations) != 0:

            current_iteration = iterations[0]
            current_iteration_name = current_iteration.publish_name

            http_endpoint = client_endpoint + "customvision/v3.0/Prediction/" + project_id + "/classify/iterations/" + current_iteration_name + "/url"

            headers = {'Prediction-Key': prediction_key, 'Content-Type': 'application/json'}
            data = {"url": data_url}
            response = requests.post(http_endpoint, headers = headers,
                                    json = data)

            response_dictionary = response.json()
            prediction = response_dictionary['predictions'][0]
            confidence = prediction['probability']
            response_dictionary['confidence'] = confidence
                
            # Display the results.
            return func.HttpResponse(json.dumps(response_dictionary))

        else:
            return f'Model not trained.'
            # return func.HttpResponse("Model not trained.", status_code=400)
    else:
        return func.HttpResponse(
             "Please pass a dataBlobUrl on the query string or in the request body",
             status_code=400
        )
