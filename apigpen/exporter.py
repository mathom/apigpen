import boto3
from botocore.exceptions import ClientError
from .exceptions import NotFoundException


def get_models(restApiId):
    api = boto3.client('apigateway')
    paginator = api.get_paginator('get_models')
    pages = paginator.paginate(restApiId=restApiId)

    models = []
    for page in pages:
        models.extend(page['items'])

    return models


def get_resources(restApiId):
    api = boto3.client('apigateway')
    paginator = api.get_paginator('get_resources')
    pages = paginator.paginate(restApiId=restApiId)

    resources = []
    for page in pages:
        resources.extend(page['items'])

    for resource in resources:
        method_names = resource.get('resourceMethods', {}).keys()
        methods = []

        for method in method_names:
            response = api.get_method(restApiId=restApiId,
                                      resourceId=resource['id'],
                                      httpMethod=method)
            del response['ResponseMetadata']
            response['methodResponses'] = response['methodResponses'].values()
            integ = response['methodIntegration']
            integ['integrationResponses'] = integ['integrationResponses'].values()
            for resp in integ['integrationResponses']:
                resp['responseTemplates'] = {
                    key: (value or '') for key,value in resp.get('responseTemplates', {}).items()
                }
                        
            methods.append(response)

        resource['resourceMethods'] = methods
            
    return resources


def get_deployments(restApiId):
    api = boto3.client('apigateway')
    paginator = api.get_paginator('get_deployments')

    pages = paginator.paginate(restApiId=restApiId)

    deployments = []
    for page in pages:
        deployments.extend(page['items'])

    for deployment in deployments:
        response = api.get_stages(restApiId=restApiId,
                                  deploymentId=deployment['id'])
        deployment['stages'] = response['item']  # strange, seems like it should be "items"
        for stage in deployment['stages']:
            del stage['deploymentId']  # waste of space
            

    return deployments


def get_authorizers(restApiId):
    api = boto3.client('apigateway')

    authorizers = []

    # blech, barely documented and no paginator
    response = api.get_authorizers(restApiId=restApiId)
    authorizers.extend(response['items'])
    while 'NextToken' in response:
        response = api.get_authorizers(restApiId=restApiId,
                                       position=response['NextToken'])
        authorizers.extend(response['items'])
        
    return authorizers

    
def export_api(name_or_id):
    api = boto3.client('apigateway')
    try:
        rest_api = api.get_rest_api(restApiId=name_or_id)
        del rest_api['ResponseMetaData']
    except ClientError as e:
        if e.response.get('Error',{}).get('Code') == 'NotFoundException':
            # try searching by name
            results = list(list_apis(name_or_id))
            if not results:
                raise NotFoundException('Could not find REST API named {0}'.format(name_or_id))
            rest_api = results[0]
        else:
            raise

    result = {
        'models': get_models(rest_api['id']),
        'resources': get_resources(rest_api['id']),
        'deployments': get_deployments(rest_api['id']),
        'authorizers': get_authorizers(rest_api['id']),
    }

    result.update(rest_api)

    return result

    
def list_apis(name=None):
    api = boto3.client('apigateway')
    pages = api.get_paginator('get_rest_apis').paginate()

    rest_apis = []
    for page in pages:
        for item in page['items']:
            if name is None or name == item['name']:
                rest_apis.append(item)

    return rest_apis