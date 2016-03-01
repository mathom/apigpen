import boto3
from .exceptions import AlreadyExistsException
from .exporter import list_apis


PREMADE_MODELS = ['Empty', 'Error']


def import_models(restApiId, models):
    api = boto3.client('apigateway')

    # delete the two models it ships with
    for model in PREMADE_MODELS:
        api.delete_model(restApiId=restApiId, modelName=model)

    for model in models:
        model = model.copy()
        del model['id']
        api.create_model(restApiId=restApiId, **model)


def import_authorizers(restApiId, authorizers):
    api = boto3.client('apigateway')
    for auth in authorizers:
        api.create_authorizer(restApiId=restApiId, **auth)


def strip_args(adict, *args):
    '''Utility to strip ids and values with None in them for boto args'''
    return {key: value for key, value in adict.items()
            if value is not None and key in args}


def import_resource(restApiId, res):
    api = boto3.client('apigateway')
    if res['path'] == '/':
        resourceId = res['id']  # root always exists
    else:
        response = api.create_resource(restApiId=restApiId,
                                       **strip_args(res, 'parentId', 'pathPart'))
        resourceId = response['id']

    for method in res['resourceMethods']:
        method = method.copy()  # don't mangle input
        methodResponses = method.pop('methodResponses', [])
        methodIntegration = method.pop('methodIntegration').copy()

        # build responses
        api.put_method(restApiId=restApiId,
                       resourceId=resourceId,
                       **method)
        for resp in methodResponses:
            api.put_method_response(restApiId=restApiId,
                                    resourceId=resourceId,
                                    httpMethod=method['httpMethod'],
                                    **resp)
        # build integrations
        integrationResponses = methodIntegration.pop('integrationResponses', [])
        integrationHttpMethod = methodIntegration.pop('httpMethod')
        api.put_integration(restApiId=restApiId,
                            resourceId=resourceId,
                            httpMethod=method['httpMethod'],
                            integrationHttpMethod=integrationHttpMethod,
                            **methodIntegration)
        for resp in integrationResponses:
            resp = resp.copy()
            api.put_integration_response(restApiId=restApiId,
                                         resourceId=resourceId,
                                         httpMethod=method['httpMethod'],
                                         **resp)

    for child in res.get('_children', []):
        child = child.copy()
        child['parentId'] = resourceId
        import_resource(restApiId, child)


def import_resources(restApiId, resources):
    api = boto3.client('apigateway')

    # we need to reorder the resources so the parent IDs work
    id_to_resource = {res['id']: res for res in resources}

    response = api.get_resources(restApiId=restApiId)
    root_id = response['items'][0]['id']

    # attach children on each dict
    root = None
    for res in resources:
        if res['path'] == '/':
            res['id'] = root_id
            root = res
        else:
            parent = id_to_resource[res['parentId']]
            parent.setdefault('_children', []).append(res)

    # traverse the tree
    if root:
        import_resource(restApiId, root)


def import_deployments(restApiId, deployments):
    api = boto3.client('apigateway')

    for deployment in sorted(deployments, key=lambda x: x['createdDate']):
        for stage in deployment.get('stages', []):
            api.create_deployment(restApiId=restApiId,
                                  **strip_args(stage,
                                               'stageName',
                                               'stageDescription',
                                               'description',
                                               'cacheClusterEnabled',
                                               'cacheClusterSize',
                                               'variables'))


def import_api(name, data):
    api = boto3.client('apigateway')

    exists = list_apis(name)

    if exists:
        raise AlreadyExistsException('A REST API named {0} already exists!'.format(name))

    response = api.create_rest_api(name=name, description=data['description'])
    restApiId = response['id']

    import_models(restApiId, data.get('models',[]))
    import_authorizers(restApiId, data.get('authorizers'.[]))
    import_resources(restApiId, data.get('resources',[]))
    import_deployments(restApiId, data.get('deployments',[]))

    return restApiId
