$subscription = 'Thaugen-semisupervised-vision-closed-loop-solution'
$location = 'westus'
$solutionNameRoot = 'MLPObjDet' # must be less than 20 characters or the storage acount variable must be provided as a constant
$modelResourceGroupName = $solutionNameRoot + 'Model'
$modelAppName = $modelResourceGroupName + 'App'
$storageAccountName = $modelResourceGroupName.ToLower() + 'strg'
$cognitiveServicesAccountName = $modelAppName
$cognitiveServicesImageAnalysisEndpoint = "https://$location.api.cognitive.microsoft.com/vision/v2.0/analyze"

# setup and configure Azure Cognitive Services Image Analysis for ML Professoar
# note double quote litterals do not seem to work when substituting parameter values from variables.  Builds the right string but it will not invoke
$command = '.\MLProfessoarModelConfig.ps1 ' +`
    '-subscription ' + $subscription + ' '+`
    '-modelResourceGroupName ' + $solutionNameRoot + 'Model ' +`
    '-modelLocation ' + $location + ' '+`
    '-modelAppName ' + $modelAppName + ' '+`
    '-modelStorageAccountName ' + $storageAccountName + ' '+`
    '-cognitiveServicesAccountName ' + $cognitiveServicesAccountName + ' '+`
    '-imageAnalysisEndpoint ' + $cognitiveServicesImageAnalysisEndpoint

$command

Invoke-Expression $command

# setupand configure ML Professoar engine for this instance of Image Analysis
$command = '.\MLProfessoarEngineConfig.ps1 ' +`
    '-subscription ' + $subscription + ' ' +`
    '-frameworkResourceGroupName ' + $solutionNameRoot + 'Engine ' +`
    '-frameworkLocation ' + $location + ' ' +`
    '-modelType Trained ' +`
    '-evaluationDataParameterName dataBlobUrl ' +`
    '-labelsJsonPath labels.regions[0].tags ' +`
    '-confidenceJSONPath confidence ' +`
    '-dataEvaluationServiceEndpoint https://' + $modelAppName + '.azurewebsites.net/api/EvaluateData ' +`
    '-confidenceThreshold .95 ' +`
    '-modelVerificationPercentage .05 ' +`
    '-trainModelServiceEndpoint https://' + $modelAppName + '.azurewebsites.net/api/TrainModel ' +`
    '-tagsUploadServiceEndpoint https://' + $modelAppName + '.azurewebsites.net/api/LoadLabelingTags ' +`
    '-LabeledDataServiceEndpoint https://' + $modelAppName + '.azurewebsites.net/api/AddLabeledData ' +`
    '-LabelingSolutionName VoTT ' +`
    '-labelingTagsParameterName labelsJson ' +`
    '-testFileCount 20'

Invoke-Expression $command
