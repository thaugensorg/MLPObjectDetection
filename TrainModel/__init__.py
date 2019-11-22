import logging
import time
import os

from datetime import datetime

import azure.functions as func

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('ML Professoar HTTP trigger function TrainModel processed a request.')

    try: 
        # Get Cognitive Services Environment Variables
        project_id = os.environ["ProjectID"]
        training_key = os.environ['TrainingKey']
        endpoint = os.environ['ClientEndpoint']
        publish_iteration_name = "SampleTreeDetection @ " + str(datetime.now())
        prediction_resource_id = os.environ['ResourceID']

    except Exception as e:
        message = str(e)
        logging.info(message)

        return func.HttpResponse(
            "Please ensure ProjectID, TrainingKey, ClientEndpoint, and ResourceID environment variables are correctly configured.",
            status_code=400
        )


    if project_id and training_key and endpoint and publish_iteration_name and prediction_resource_id:
        trainer = CustomVisionTrainingClient(training_key, endpoint=endpoint)

        try:
            iteration = trainer.train_project(project_id, force_train=True)
            while (iteration.status != "Completed"):
                iteration = trainer.get_iteration(project_id, iteration.id)
                logging.info("Training status: " + iteration.status)
                time.sleep(1)

            # The iteration is now trained. Publish it to the project endpoint
            trainer.publish_iteration(project_id, iteration.id, publish_iteration_name, prediction_resource_id)

        except Exception as e:
            message = str(e)
            logging.info(message)
            
            return func.HttpResponse(
                "Training failed for ProjectID: " + project_id + " could not be trained with message: " + message,
                status_code=400)

        return func.HttpResponse(
            "Training complete for ProjectID: " + project_id + " published under iteration name: " + publish_iteration_name,
            status_code=200)

    else:
        return func.HttpResponse(
            "Please ensure ProjectID, TrainingKey, ClientEndpoint, and ResourceID environment variables are correctly configured.",
            status_code=400
        )
