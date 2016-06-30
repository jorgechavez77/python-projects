# MMC

import json
import requests
import logging
import sys

# from lib import logger

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


def json_pretty_print(string):
    return json.dumps(string, indent=2)


def get_auth():
    auth = ('admin', 'admin')
    return auth


def get_servers():

    logger.info('Get servers')
    logger.info('URL: ' + URL_SERVER)
    response = requests.get(URL_SERVER, auth=get_auth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))

    if status_code == 200:
        json_data = response.json()
        return json_data

    logger.error(response.text)
    return ''


def get_servers_by_group(group_id):

    logger.info('Get servers by group')
    url = URL_SERVER + '?groupId=' + group_id
    logger.info('URL: ' + url)
    response = requests.get(url, auth=get_auth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))

    if status_code == 200:
        json_data = response.json()
        return json_data

    logger.error(response.text)
    return ''        


def get_server_id_by_name(name):

    logger.info('Get serverId by name')
    json_data = get_servers()
    servers = json_data['data']
    for server in servers:
        if server['name'] == name:
            logger.info('href: ' + server['href'])
            return server['id']
            
    logger.error('Server ' + name + ' not found')
    return ''


def get_repositories():
    
    logger.info('Get repositories')
    response = requests.get(URL_REPO, auth=get_auth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))

    if status_code == 200:
        json_data = response.json()
        return json_data

    logger.error(response.text)
    return ''


def get_repository_by_name_version(p_name, p_version):

    logger.info('Get repository by name')
    json_data = get_repositories()
    repositories = json_data['data']
    for repo in repositories:
        if repo['name'] == p_name:
            versions = repo['versions']
            for version in versions:
                if version['name'] == p_version:
                    return version['id']

    logger.error('version not found in repo ' + p_name)
    return ''


def repository_upload_file(p_file, p_name, p_version):
    
    logger.info('Repository upload file')
    files = {'file': open(p_file, 'rb'), 'name': p_name, 'version' : p_version}
    response = requests.post(URL_REPO, files=files, auth=get_auth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))

    if status_code == 200:
        json_data = response.json()
        return json_data

    logger.error(response.text)
    return ''


def repository_delete_file(p_version):

    logger.info('Repository delete file')
    url_delete = URL_REPO + '/' + p_version
    logger.info('URL: ' + url_delete)
    response = requests.delete(url_delete, auth=get_auth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))
    
    if status_code == 200:
        logger.info('File ' + p_version + ' deleted')
        text_data = response.text
        return text_data
    elif status_code == 405:
        return 'Not found to delete'

    logger.error(response.text)
    return ''


def create_deployment(p_name, p_version, p_server):

    logger.info('Create deployment')
    payload = {'name': p_name, 'servers': [p_server], 'applications': [p_version]}
    logger.info(json.dumps(payload, indent=2))
    response = requests.post(URL_DEPLOY, json=payload, auth=get_auth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))

    if status_code == 200:
        json_data = response.json()
        return json_data

    logger.error(response.text)
    return ''


def get_deployments():

    logger.info('Get deployments')
    logger.info('URL: ' + URL_DEPLOY)
    response = requests.get(URL_DEPLOY, auth=get_auth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))

    if status_code == 200:
        json_data = response.json()
        return json_data

    logger.error(response.text)
    return ''    


def get_deployment_id_by_name(p_name):
    
    logger.info('Get deployment by name')
    json_data = get_deployments()
    deployments = json_data['data']
    for deploy in deployments:
        if deploy['name'] == p_name:
            return deploy['id']

    logger.error('Deployment name ' + p_name + 'not found')
    return ''


def get_deployment_href_by_name(p_name):
    logger.info('Get deployment by name')
    json_data = get_deployments()
    deployments = json_data['data']
    for deploy in deployments:
        if deploy['name'] == p_name:
            return deploy['href']

    logger.error('Deployment name ' + p_name + 'not found')
    return ''


def delete_deployment_by_href(href):
    logger.info('Delete deployment')
    url_delete = href

    logger.info('URL: ' + url_delete)
    response = requests.delete(url_delete, auth=get_auth())
    status_code = response.status_code
    logger.info('status code: ' + str(status_code))

    if status_code == 200:
        text_data = response.text
        return text_data

    logger.error(response.text)
    return ''


# Find Application version in the MMC Repository
def get_file_from_repository(app_name, app_version):

    logger.info('Get Repo: ' + app_name + ' ' + app_version)
    version_id = ''
    headers = {'Content-Type': 'application/json'}
    response = requests.get(URL_REPO, headers=headers, auth=('admin', 'admin'))
    
    #logger.info('Response: ' + response.text)
    json_data = response.json()
    logger.info(json.dumps(json_data, indent=2))
    array = json_data['data']
    for a in array:
        if a['name'] == app_name:
            versions = a['versions']
            for version in versions:
                if version['name'] == app_version:
                    logger.info('Found app version: ' + version['id'])
                    version_id = version['id']
    return version_id


# Delete application version from MMC Repository
def delete_file(v):

    logger.info('Delete: ' + v)
    url_delete = URL_REPO + '/' + v

    logger.info('URL: ' + url_delete)
    response = requests.delete(url_delete, auth=('admin', 'admin'))
    
    text_response = response.text
    logger.info(text_response)
    # Pending to review when it fails to delete
    #result = response.text
    #logger('Delete response: ' + result)
    #json_data = response.json()
    #logger.info(json.dumps(json_data, indent=2))


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
    json_data = response.json()

    logger.info(json.dumps(json_data, indent=2))
    # Pending to validate file upload
    
    app_id = json_data['applicationId']
    return app_id


#def create_deployment(app_name, app_version, server):

#    logger.info('Create Deployment: ' + server + ' ' + app_name + ' ' + app_version)

#    payload = { 'name' : app_name, 'servers' : [ server ], 'applications' : [ app_version ] }
#    logger.info(json.dumps(payload, indent=2))

#    response = requests.post(URL_DEPLOY, json=payload, auth=('admin', 'admin'))
    
#    logger.info('TEXT: ' + response.text)
#    json_data = response.json()
#    logger.info(json.dumps(json_data, indent=2))

#    url = json_data['href']


# def find_deployment():
def deployment(filename, appname, appversion, server):
    
    server_id = get_server(server)
    version_id = get_file_from_repository(appname, appversion)
    #app_id = ''

    if version_id != '':
        logger.info('versionId: ' + version_id)
        delete_file(version_id)

    upload_file(filename, appname, appversion)

    app_id = get_file_from_repository(appname, appversion)
    
    deployment_url = ''
    if app_id != '':
        deployment_url = create_deployment(appname, app_id, server_id)
    
    if deployment_url != '':
        logger.info('Deploy URL: ' + deployment_url)
        url = deployment_url + '/deploy'
        logger.info('URL: ' + url)
        response = requests.post(url, auth=('admin', 'admin'))
        json_data = response.json()
        logger.info('Deploy...')
        logger.info(json.dumps(json_data, indent=2))

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

servers = get_servers()
logger.info(json_pretty_print(servers))

servers = get_servers_by_group('Development')
logger.info(json_pretty_print(servers))

serverId = get_server_id_by_name('localhost')
logger.info(serverId)

repositories = get_repositories()
logger.info(json_pretty_print(repositories))

repository = get_repository_by_name_version('mule-example-hello', '3.4.2')
logger.info(repository)

delete = repository_delete_file(repository)
logger.info(delete)

upload = repository_upload_file('mule-example-hello-3.4.2.zip', 'mule-example-hello', '3.4.2')
logger.info(json_pretty_print(upload))

versionId = upload['versionId']
deploy = create_deployment('deploy-mule-example-hello', versionId, serverId)

deployments = get_deployments()
logger.info(json_pretty_print(deployments))

deploymentId = get_deployment_id_by_name('deploy-mule-example-hello')
logger.info(deploymentId)

deploymentHref = get_deployment_href_by_name('deploy-mule-example-hello')
logger.info(deploymentHref)

deleteDeploy = delete_deployment_by_href(deploymentHref)
logger.info(deleteDeploy)
