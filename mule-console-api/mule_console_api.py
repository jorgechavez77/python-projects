# MMC

import json, requests, sys

# from lib import logger

import logging

# create logger
logger = logging.getLogger("mmc_deploy")
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

###############################
#          Global variables   #
###############################

PATH = 'http://axf3023.axcess-financial.com:8080/mmc-console-3.6.2/api/'
URL_REPO = PATH + 'repository'
URL_SERVER = PATH + 'servers'
URL_DEPLOY = PATH + 'deployments'

################################
#          Functions           #
################################

def jsonPrettyPrint(string):
    return json.dumps(string, indent=2)

def getAuth():
    auth = ('admin', 'admin')
    return auth

def getServers():

    logger.info('Get servers')
    logger.info('URL: ' + URL_SERVER)
    response = requests.get(URL_SERVER, auth=getAuth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))

    if status_code == 200:
        jsonData = response.json()
        return jsonData

    logger.error(response.text)
    return ''

def getServersByGroup(groupId):

    logger.info('Get servers by group')
    url = URL_SERVER + '?groupId=' + groupId
    logger.info('URL: ' + url)
    response = requests.get(url, auth=getAuth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))

    if status_code == 200:
        jsonData = response.json()
        return jsonData

    logger.error(response.text)
    return ''        

def getServerIdByName(name):

    logger.info('Get serverId by name')
    jsonData = getServers()
    servers = jsonData['data']
    for server in servers:
        if server['name'] == name:
            logger.info('href: ' + server['href'])
            return server['id']
            
    logger.error('Server ' + name + ' not found')
    return ''

def getRepositories():
    
    logger.info('Get repositories')
    response = requests.get(URL_REPO, auth=getAuth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))

    if status_code == 200:
        jsonData = response.json()
        return jsonData

    logger.error(response.text)
    return ''

def getRepositoryByNameVersion(p_name, p_version):

    logger.info('Get repository by name')
    jsonData = getRepositories()
    repositories = jsonData['data']
    for repo in repositories:
        if repo['name'] == p_name:
            versions = repo['versions']
            for version in versions:
                if version['name'] == p_version:
                    return version['id']

    logger.error('version not found in repo ' + p_name)
    return ''

def repositoryUploadFile(p_file, p_name, p_version):
    
    logger.info('Repository upload file')
    files = {'file': open(p_file, 'rb'), 'name': p_name, 'version' : p_version}
    response = requests.post(URL_REPO, files=files, auth=getAuth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))

    if status_code == 200:
        jsonData = response.json()
        return jsonData

    logger.error(response.text)
    return ''

def repositoryDeleteFile(p_version):

    logger.info('Repository delete file')
    URL_DELETE = URL_REPO + '/' + p_version
    logger.info('URL: ' + URL_DELETE)
    response = requests.delete(URL_DELETE, auth=getAuth())    
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))
    
    if status_code == 200:
        logger.info('File ' + p_version + ' deleted')
        textData = response.text
        return textData
    elif status_code == 405:
        return 'Not found to delete'

    logger.error(response.text)
    return ''

def createDeployment(p_name, p_version, p_server):

    logger.info('Create deployment')
    payload = { 'name' : p_name, 'servers' : [ p_server ], 'applications' : [ p_version ] }
    logger.info(json.dumps(payload, indent=2))
    response = requests.post(URL_DEPLOY, json=payload, auth=getAuth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))

    if status_code == 200:
        jsonData = response.json()
        return jsonData

    logger.error(response.text)
    return ''

def getDeployments():

    logger.info('Get deployments')
    logger.info('URL: ' + URL_DEPLOY)
    response = requests.get(URL_DEPLOY, auth=getAuth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))

    if status_code == 200:
        jsonData = response.json()
        return jsonData

    logger.error(response.text)
    return ''    

def getDeploymentIdByName(p_name):
    
    logger.info('Get deployment by name')
    jsonData = getDeployments()
    deployments = jsonData['data']
    for deploy in deployments:
        if deploy['name'] == p_name:
            return deploy['id']

    logger.error('Deployment name ' + p_name + 'not found')
    return ''

def getDeploymentHrefByName(p_name):
    logger.info('Get deployment by name')
    jsonData = getDeployments()
    deployments = jsonData['data']
    for deploy in deployments:
        if deploy['name'] == p_name:
            return deploy['href']

    logger.error('Deployment name ' + p_name + 'not found')
    return ''

def deleteDeploymentByHref(href):
    logger.info('Delete deployment')
    URL_DELETE = href

    logger.info('URL: ' + URL_DELETE)
    response = requests.delete(URL_DELETE, auth=getAuth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))

    if status_code == 200:
        textData = response.text
        return textData

    logger.error(response.text)
    return ''

# Find Application version in the MMC Repository
def get_file_from_repository(app_name, app_version):

    logger.info('Get Repo: ' + app_name + ' ' + app_version)
    versionId = ''
    headers = {'Content-Type': 'application/json'}
    response = requests.get(URL_REPO, headers=headers, auth=('admin', 'admin'))
    
    #logger.info('Response: ' + response.text)
    jsonData = response.json()
    logger.info(json.dumps(jsonData, indent=2))
    array = jsonData['data']
    for a in array:
        if a['name'] == app_name:
            versions = a['versions']
            for version in versions:
                if version['name'] == app_version:
                    logger.info('Found app version: ' + version['id'])
                    versionId = version['id']
    return versionId

# Delete application version from MMC Repository
def delete_file(v):

    logger.info('Delete: ' + v)
    URL_DELETE = URL_REPO + '/' + v

    logger.info('URL: ' + URL_DELETE)
    response = requests.delete(URL_DELETE, auth=('admin', 'admin'))
    
    textResponse = response.text
    logger.info(textResponse)    
    # Pending to review when it fails to delete
    #result = response.text
    #logger('Delete response: ' + result)
    #jsonData = response.json()
    #logger.info(json.dumps(jsonData, indent=2))

# Upload app version to MMC Repository
def upload_file(f, n, v):
    
    logger.info('Upload: ' + n + ' ' + v)
    # find app version
    #versionId = get_repo(n, v)

    #logger.info('versionId: ' + versionId)
    #if versionId != '':
    #    delete(versionId)

    files = {'file': open(f, 'rb'), 'name': n, 'version' : v}
    response = requests.post(URL_REPO, files=files, auth=('admin', 'admin'))
    #logger.info('Response: ' + response.text)
    jsonData = response.json()

    logger.info(json.dumps(jsonData, indent=2))
    # Pending to validate file upload
    
    appId = jsonData['applicationId']
    return appId

def create_deployment(app_name, app_version, server):

    logger.info('Create Deployment: ' + server + ' ' + app_name + ' ' + app_version)

    payload = { 'name' : app_name, 'servers' : [ server ], 'applications' : [ app_version ] }
    logger.info(json.dumps(payload, indent=2))

    response = requests.post(URL_DEPLOY, json=payload, auth=('admin', 'admin'))
    
    logger.info('TEXT: ' + response.text)
    jsonData = response.json()
    logger.info(json.dumps(jsonData, indent=2))

    url = jsonData['href']

# def find_deployment():
    
def deployment(filename, appname, appversion, server):
    
    serverId = get_server(server)
    versionId = get_file_from_repository(appname, appversion)
    appId = ''

    if versionId != '':
        logger.info('versionId: ' + versionId)
        delete_file(versionId)

    upload_file(filename, appname, appversion)

    appId = get_file_from_repository(appname, appversion)
    
    deploymentUrl = ''
    if appId != '':
        deploymentUrl = create_deployment(appname, appId, serverId)
    
    if deploymentUrl != '':
        logger.info('Deploy URL: ' + deploymentUrl)
        url = deploymentUrl + '/deploy'
        logger.info('URL: ' + url)
        response = requests.post(url, auth=('admin', 'admin'))
        jsonData = response.json()
        logger.info('Deploy...')
        logger.info(json.dumps(jsonData, indent=2))

    logger.info('End')

#Execution
#print 'Enter filename:'
#filename = raw_input()
#print 'Enter app name:'
#appname = raw_input()
#print 'Enter app version:'
#appversion = raw_input()
#print 'Enter server:'
#server = raw_input()

servers = getServers()
logger.info(jsonPrettyPrint(servers))

servers = getServersByGroup('Development')
logger.info(jsonPrettyPrint(servers))

serverId = getServerIdByName('localhost')
logger.info(serverId)

repositories = getRepositories()
logger.info(jsonPrettyPrint(repositories))

repository = getRepositoryByNameVersion('mule-example-hello', '3.4.2')
logger.info(repository)

delete = repositoryDeleteFile(repository)
logger.info(delete)

upload = repositoryUploadFile('mule-example-hello-3.4.2.zip', 'mule-example-hello', '3.4.2')
logger.info(jsonPrettyPrint(upload))

versionId = upload['versionId']
deploy = createDeployment('deploy-mule-example-hello', versionId, serverId)

deployments = getDeployments()
logger.info(jsonPrettyPrint(deployments))

deploymentId = getDeploymentIdByName('deploy-mule-example-hello')
logger.info(deploymentId)

deploymentHref = getDeploymentHrefByName('deploy-mule-example-hello')
logger.info(deploymentHref)

deleteDeploy = deleteDeploymentByHref(deploymentHref)
logger.info(deleteDeploy)
