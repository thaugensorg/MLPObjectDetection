$subscription = 'Thaugen-semisupervised-vision-closed-loop-solution'
$location = 'westus'
$solutionNameRoot = 'MLPObjDet' # must be less than 20 characters or the storage acount variable must be provided as a constant
$modelAppName = $solutionNameRoot + 'ModelApp'
$storageAccountName = $solutionNameRoot.ToLower() + 'strg'
$cognitiveServicesAccountName = $modelAppName
$cognitiveServicesImageAnalysisEndpoint = "https://$location.api.cognitive.microsoft.com/vision/v2.0/analyze"
#$imageAnalysisVisualFeatures = 'Categories,Description,Color,Brands' *****TODO***** figure out hose to pass a string that includes a comma

# setupand configure ML Professoar engine for this instance of Image Analysis
$command = '.\MLProfessoarEngineConfig.ps1 ' +`
    '-subscription ' + $subscription + ' '+`
    '-frameworkResourceGroupName ' + $solutionNameRoot + 'Engine ' +`
    '-frameworkLocation ' + $location + ' '+`
    '-modelType Trained ' +`
    '-evaluationDataParameterName dataBlobUrl ' +`
    '-labelsJsonPath labels.regions[0].tags ' +`
    '-confidenceJSONPath confidence ' +`
    '-dataEvaluationServiceEndpoint https://$modelAppName.azurewebsites.net/api/EvaluateData ' +`
    '-confidenceThreshold .95 ' +`
    '-modelVerificationPercentage .05 ' +`
    '-trainModelServiceEndpoint https://' + $modelAppName + '.azurewebsites.net/api/TrainModel ' +`
    '-tagsUploadServiceEndpoint https://' + $modelAppName + '.azurewebsites.net/api/LoadLabelingTags ' +`
    '-LabeledDataServiceEndpoint https://' + $modelAppName + '.azurewebsites.net/api/AddLabeledData ' +`
    '-LabelingSolutionName VoTT ' +`
    '-labelingTagsParameterName labelsJson ' +`
    '-testFileCount 30'

Invoke-Expression $command