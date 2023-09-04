#
# =======================================
# AUTHORS       : Claudio Prato @TeamEA
#               : Serena Sensini @TeamEA
# DATE          : 2023/09/01
# PURPOSE       : 
# SPECIAL NOTES : 
#               : 
# =======================================
#

# import logging
import posix
from InquirerPy import prompt
from prompt_toolkit.validation import Validator, ValidationError
import re
import sys
import subprocess
from subprocess import PIPE
import json
import os
# import signal
import docker, boto3, botocore, base64

from os.path import exists

print("################")
print("Ready to migrate from Openshift Template 2 Helm?")
print("Insert all the required information and wait for the output...")
print("################")


class AccessKeyIDValidator(Validator):

    def contains_symbols(self, value):
        regex = re.compile('((?:ASIA|AKIA|AROA|AIDA)([A-Z0-7]{16}))')
        is_match = regex.match(value) is not None
        return is_match

    def validate(self, document):
        try:
            check = document.text
            if not self.contains_symbols(check):
                raise ValueError
        except ValueError:
            raise ValidationError(
                message="Please enter a valid Access Key ID. Only upper case alphanumeric characters.",
                cursor_position=len(document.text))

class SecretAccessKeyValidator(Validator):

    def contains_symbols(self, value):
        regex = re.compile('([a-zA-Z0-9+/]{40})')
        is_match = regex.match(value) is not None
        return is_match

    def validate(self, document):
        try:
            check = document.text.lower()
            if not self.contains_symbols(check):
                raise ValueError
        except ValueError:
            raise ValidationError(
                message="Please enter a valid Secret Access Key. A string of 40 digits is expected; only upper case alphanumeric characters, and '+' or '/' symbols are admitted.",
                cursor_position=len(document.text))

class GitHubPat(Validator):

    def contains_symbols(self, value):
        regex = re.compile('(github_pat_[\w\W]+)')
        is_match = regex.match(value) is not None
        return is_match

    def validate(self, document):
        try:
            check = document.text.lower()
            if not self.contains_symbols(check):
                raise ValueError
        except ValueError:
            raise ValidationError(
                message="Please enter a valid GitHub PAT. A string begining with 'github_pat_' prefix is expected; alphanumeric characters, and '+' or '/' symbols are admitted.",
                cursor_position=len(document.text))

class PathValidator(Validator):

    def contains_symbols(self, value):
        regex = re.compile('^[A-Za-z0-9-_/.]+$')
        is_match = regex.match(value) is not None
        return is_match

    def validate(self, document):
        try:
            check = document.text.lower()
            if not self.contains_symbols(check):
                raise ValueError
        except ValueError:
            raise ValidationError(
                message="Please enter a valid path, with no trailing spaces.",
                cursor_position=len(document.text))

class StringValidator(Validator):

    def contains_symbols(self, value):
        regex = re.compile('^[A-Za-z0-9-_]+$')
        is_match = regex.match(value) is not None
        return is_match

    def validate(self, document):
        try:
            check = document.text.lower()
            if not self.contains_symbols(check):
                raise ValueError
        except ValueError:
            raise ValidationError(
                message="Please enter a valid string, with no trailing spaces.",
                cursor_position=len(document.text))

class AccountIDValidator(Validator):

    def contains_symbols(self, value):
        regex = re.compile('^\d{12}$')
        is_match = regex.match(value) is not None
        return is_match

    def validate(self, document):
        try:
            check = document.text.lower()
            if not self.contains_symbols(check):
                raise ValueError
        except ValueError:
            raise ValidationError(
                message="Please enter a valid Account ID. Only 12 digits are admitted.",
                cursor_position=len(document.text))

# 
# ::: Global Functions
# 

def is_installed(name):
    """Check whether `name` is on PATH and marked as executable"""
    
    from shutil import which
    
    return which(name) is not None

def runcmd_call(cmd):
    try:
        p = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as suberr:
        p = suberr.returncode
        print('\n::: ERROR ::: \n' + print(suberr.stdout))
    except Exception as e:
        print(e)
    return p

questions = [
    {
        "type": "input",
        "message": "Access Key ID:",
        "name": "access_key_id",
        "validate": AccessKeyIDValidator()
    },
    {
        "type": "input",
        "message": "Secret Access Key:",
        "name": "secret_access_key",
        "validate": SecretAccessKeyValidator()
    },
    {
        "type": "list",
        "message": "Region:",
        "choices": ["eu-central-1", "eu-west-1", "eu-west-2", "eu-south-1", "eu-west-3", "eu-south-2", "eu-north-1",
                    "eu-central-2"],
        "name": "region"
    },
    {
        "type": "input",
        # 350801433917.dkr.ecr.eu-west-1.amazonaws.com/enterprise-architect/ea-project-skeleton/sample-webapp:1.6.1-SNAPSHOT
        "message": "Type the Target Image:",
        "name": "target_image",
        # "validate": StringValidator() - set a validator
    },
    {
        "type": "input",
        # public.ecr.aws/dedalus-ea/ea-utils:latest
        "message": "Type the Utility Image:",
        "name": "utility_image",
    },
    {
        "type": "input",
        # /opt/dedalus/projects/ea-project-skeleton/sample-webapp-oci/
        "message": "Project Root Directory:",
        "name": "project_root_directory",
        "validate": PathValidator()
    },
    {
        # dedalus.template.yml
        "type": "input",
        "message": "Openshift Template File Name (type the file name stored within the target image on the path: '/opt/dedalus/template'):",
        "name": "src_template_name",
        "validate": PathValidator()
    },
    {
        "type": "input",
        "message": "Helm Charts Directory Name:",
        "name": "helm_chart_name",
        "validate": PathValidator()
    },
    # {
    #     "type": "input",
    #     # [project_root_directory]/
    #     "message": "Helm Charts Package Directory:",
    #     "name": "helm_charts_package_dir",
    #     "validate": PathValidator()
    # },
    # {
    #     "type": "input",
    #     "message": "Type the local/remote Helm Charts Package Name without the version:",
    #     "name": "helm_charts_package_name"
    # },  
    {
        "type": "input",
        "message": "Project Version:",
        "name": "project_version"
        # "validate": StringValidator()
    },
    {
        "type": "input",
        "message": "Type the GitHub Personal Access Token:",
        "name": "github_pat",
        "validate": GitHubPat()
    },
    {
        "type": "confirm", "message": "Confirm?",
        "name": "confirmation"
    }
]

use_config = [
    {
        "type": "confirm", "message": "File config.json with some configuration found. Use this file to proceed?",
        "name": "confirmation"
    },
]

def prompt_questions(questions):
    result = prompt(questions)
    if result["confirmation"]:
        print("Proceeding with inserted data.")
        return result
    else:
        print("To enter again the data, re-run the script. Bye!")
        sys.exit()

def clean_containers(docker_client, container_name):
    '''
    Cleaning the system by containers created previously
    '''
    
    try:
        cont_obj = docker_client.containers.get(container_name)
        if cont_obj :
            print('::: INFO - removing the container: ' + cont_obj.short_id)
            cont_obj.remove(v=True,force=True)
    except docker.errors.NotFound as e:
        print('::: INFO - the system is clean as well. The container was not found.')
    except docker.errors.APIError as e:
        print('::: ERROR this is the message: {}'.format(e))
        sys.exit(-1)

def create_kubeconfig():
    ''' Building a Kubeconfig Template'''
    
    import yaml

    kubeconfig = {
        'apiVersion': 'v1',
        'clusters': [
            {
                'name': 'fake-cluster',
                'cluster': {
                    'server': 'https://cluster-api-server-url'
                }
            }
        ],
        'contexts': [
            {
                'name': 'fake-context',
                'context': {
                    'cluster': 'fake-cluster',
                    'user': 'fake-user',
                    'namespace': 'default'
                }
            }
        ],
        'current-context': 'fake-context',
        'kind': 'Config',
        'preferences': {},
        'users': [
            {
                'name': 'fake-user'
            }
        ]
    }
    
    try:
        yaml_str = yaml.dump(kubeconfig)
        return(yaml_str)                
    except Exception as e:
        print(e)
        sys.exit()

        
def get_aws_token(result):
    
    # initialize vars
    aws_token_obj = {}
    
    ecr_client = boto3.client('ecr',
                              aws_access_key_id=result["access_key_id"], 
                              aws_secret_access_key=result["secret_access_key"], 
                              region_name=result["region"]
                              )
    
    try:
        aws_token = ecr_client.get_authorization_token()
    except botocore.exceptions.ClientError as e:
        print('::: ERROR - the error message is: {}'.format(e.response['Error']['Message']))
        sys.exit(-1)
    except Exception as e:
        print(e)
        sys.exit()

    aws_token_obj['username'], aws_token_obj['password'] = base64.b64decode(aws_token['authorizationData'][0]['authorizationToken']).decode().split(':')
    
    # docker python module open issue: without workaround
    # aws_token_obj['registry'] = aws_token['authorizationData'][0]['proxyEndpoint']
    
    # docker python module open issue: workaround
    aws_token_obj['registry'] = aws_token['authorizationData'][0]['proxyEndpoint'].replace("https://", "")
    for aws_item_key in aws_token_obj:
        print("::: INFO - the '" + aws_item_key + "': '" + aws_token_obj[aws_item_key] + "'")

    if type(aws_token_obj) != dict:
        print("::: ERROR - Return code:", aws_token_obj)
        print(
            "The AWS token object is empty. Check your AWS Keys to get more details")
        sys.exit(-1)

    return aws_token_obj

def get_oc_template(result, aws_token_obj, docker_client):
    '''
    Getting the Openshift Template from the target image
    '''
    
    clean_containers(docker_client, 'get_oc_template')
    
    docker_client.login(aws_token_obj['username'], aws_token_obj['password'], registry=aws_token_obj['registry'])
    # docker_client.images.pull(result["target_image"])
        
    # ::: Setup the working container
    try:
        container = docker_client.containers.run(result["utility_image"],
                    ['tail',
                    '-f',
                    '/dev/null'],
                    detach=True,
                    environment= [
                        # 'KUBECONFIG=/root/.kube/config'
                        'KUBECONFIG=/workspace/.kubeconfig'
                        ],
                    name='get_oc_template',
                    user=os.getuid(),
                    volumes = [
                        # os.path.expanduser( '~' ) + '/.kube:/root/.kube',
                        result["project_root_directory"] + ':/workspace'
                    ]
                    )
        
        # ::: add here the step you require
        steps = {
            # step 1 - build a fake kubeconfig
            'create_kubeconfig': {
                'cmd':["bash","-c","echo -e '" + create_kubeconfig() + "' > /workspace/.kubeconfig"],
                'msg':'::: INFO - build the /workspace/.kubeconfig inside the container.'
            },
            # step 2 - aws ecr registry login
            'registry_login': {
                'cmd':["oc","registry","login","--registry","350801433917.dkr.ecr.eu-west-1.amazonaws.com","--auth-basic=AWS:" + aws_token_obj["password"],"--insecure=true"],
                'msg':'::: INFO - run the AWS Registry Login command.'
            },
            # step 3 - extracting the openshift template
            'oc_extract': {
                'cmd':["oc","image","extract",result["target_image"],"--path","/opt/dedalus/templates/" + result["src_template_name"] + ":/workspace","--insecure=true","--confirm=true"],
                'msg':'::: INFO - getting the Openshift Template: ' + result["src_template_name"] + ' from the Target Image: ' + result["target_image"]
            },
            # step 4 - build a fake kubeconfig
            'remove_kubeconfig': {
                'cmd':["bash","-c","rm -rf /workspace/.kubeconfig"],
                'msg':'::: INFO - delete the /workspace/.kubeconfig.'
            }
        }
        
        for step in steps:
            ''' it run the actions into a temporary container '''
            
            str_cmd = ' '.join(steps[step]['cmd'])
            print(steps[step]['msg'] + "\nThe command is being run:\n###\n" + str_cmd + '\n###\n')
            docker_cmd_res = container.exec_run(
                                steps[step]['cmd'],
                                tty=True
                            )
            if docker_cmd_res.exit_code != 0 :
                print("::: ERROR - return code:", docker_cmd_res.exit_code)
                print(
                    "::: ERROR - failing during the execution with message: " + docker_cmd_res.output.decode("utf-8"))
                sys.exit(1)
            
            if docker_cmd_res.output:
                print("::: INFO :::\n" + docker_cmd_res.output.decode("utf-8"))
        
        # ::: cleaning the environment
        print('::: INFO - removing the container: ' + container.short_id)
        container.remove(v=True,force=True)
   
    # except docker.errors.ContainerError as e:
    #     print('::: ERROR the container return the following error message: {}'.format(e.response['Error']['Message']))
    #     sys.exit(-1)
    except docker.errors.ImageNotFound as e:
        print('::: ERROR - the docker image was not found: {}'.format(e.response['Error']['Message']))
        sys.exit(-1)
    except docker.errors.APIError as e:
        print('::: ERROR - this is the message: {}'.format(e))
        sys.exit(-1)
    except Exception as e:
        print(e)
        sys.exit()
        
def template2helm(result):
    '''
    Converting the openshift template to helm package
    '''
    
    docker_client = docker.from_env()
    clean_containers(docker_client, 'template2helm')
    
    try:
        docker_client.containers.run(result["utility_image"],
                        ["template2helm",
                        "convert",
                        "--template",
                        "/workspace/" + result["src_template_name"],
                        "--chart",
                        "/workspace/"],
                        name='template2helm',
                        auto_remove=True,
                        user=os.getuid(),
                        volumes = [result["project_root_directory"] + ':/workspace']
                        )
                        # ).decode("utf-8")
    # except docker.errors.ContainerError as e:
    #     print('::: ERROR the container return the following error message: {}'.format(e.response['Error']['Message']))
    #     sys.exit(-1)
    except docker.errors.ImageNotFound as e:
        print('::: ERROR - the docker image was not found: {}'.format(e.response['Error']['Message']))
        sys.exit(-1)
    except docker.errors.APIError as e:
        # print('::: ERROR the Docker Server Error message is: {}'.format(e.response['Error']['Message']))
        print('::: ERROR - This is the message: {}'.format(e))
        sys.exit(-1)
    except Exception as e:
        # print(e)
        print(f'\n::: Command:\n{e.command}\nError:\n {e.stderr}')
        sys.exit()
  
def helm_package(action, result, docker_client):
    ''' Helm Actions '''
        
    if action == 'helm_create_package':
        cmd = ['helm',
            'package',
            '--dependency-update',
            result["project_root_directory"] + "/" + result["helm_chart_name"],
            '--version', result["project_version"],
            '--app-version', result["project_version"],
            '--destination', result["project_root_directory"]
            ]

        print('::: INFO - The Helm Package Command is: ' + ' '.join(cmd))

        res = runcmd_call(cmd)
        if type(res) == int:
            print("::: ERROR - the return code is:", res)
            print(
                "::: ERROR - failing during the execution.")
            sys.exit(-1)
        
        print('::: INFO - the Helm Package creation output is: ' + res.decode("utf-8"))
        
    elif action == 'helm_push_package':
        clean_containers(docker_client, 'helm_push_package')

        try:
            docker_client.containers.run(result["utility_image"],
                            ["helm-git-push",
                            "-p",
                            "/workspace/" + result["helm_chart_name"] + "-" + result["project_version"] + ".tgz",
                            "-f",
                            result["helm_chart_name"] + result["project_version"] + ".tgz"],
                            # auto_remove=True,
                            environment  = ["GITHUB_PAT=" + result["github_pat"] ],
                            name='helm_push_package',
                            # stream=True,
                            user=os.getuid(),
                            volumes = [result["project_root_directory"] + ":/workspace"],
                            # tty=True
                            ).decode("utf-8")

        # except docker.errors.ContainerError as e:
        #     print('::: ERROR - the container return the following error message: {}'.format(e.response['Error']['Message']))
        #     sys.exit(-1)
        except docker.errors.ImageNotFound as e:
            print('::: ERROR - the docker image was not found: {}'.format(e.response['Error']['Message']))
            sys.exit(-1)
        except docker.errors.APIError as e:
            # print('::: ERROR - the Docker Server Error message is: {}'.format(e.response['Error']['Message']))
            print(f'::: ERROR - this is the message: {e}')
            sys.exit(-1)
        except Exception as e:
            # print(e)
            print(f'\n::: Command:\n{e.command}\nError:\n {e.stderr}')
            sys.exit()
            
        print('::: INFO - the Helm Package is going to push is: ' + result["helm_chart_name"] + result["project_version"] + '.tgz')

def getuid() -> int:
    if posix:
        return os.getuid()
    return 0

def main():

    # Step 0: preparing the environment
    result = None
    try:
        #  docker_client = docker.from_env(version='1.24')
        docker_client = docker.from_env()
    except docker.errors.ImageNotFound as e:
        print('::: ERROR - the docker image was not found: {}'.format(e.response['Error']['Message']))
        sys.exit(-1)
    except docker.errors.APIError as e:
        print('::: ERROR - this is the message: {}'.format(e))
        sys.exit(-1)
    except Exception as e:
        print(e)
        sys.exit()

    # ::: check the script requirements
    packages = ['docker', 'helm']
    for package_name in packages:
        res = is_installed(package_name)
        if res is not True:
            print("::: ERROR - error during the execution. The tool: " + package_name + " is not installed in your system! Please install it before run the script again.")
            return 1
    
    # ::: check the script configuration file
    try:
        with open('config.json') as file:
            file_exists = exists("config.json")
            file_empty = False if os.stat("config.json").st_size == 0 else True
            json_object = json.load(file)
            if file_exists and file_empty != False and json_object and len(json_object) > 0:
                result = prompt(use_config)
                if result["confirmation"]:
                    print("::: INFO - Proceeding with existing data in config.json.")
                    result = json_object
                else:
                    result = prompt_questions(questions)
            else:
                result = prompt_questions(questions)

    except KeyboardInterrupt:
        print("::: INFO - User exited. Bye!")
    except FileNotFoundError as e:
        result = prompt_questions(questions)
    except Exception as e:
        print(e)
        print("::: ERROR - syntax error in config.json. Lint that file or REMOVE it!")
        sys.exit()

    # Store file for future use
    json_object = json.dumps(result, indent=4)

    with open("config.json", "w") as outfile:
        outfile.write(json_object)

    # step 1 - get the aws ecr token
    aws_token_obj = get_aws_token(result)
    
    # step 2 - getting the Openshift Template
    get_oc_template(result, aws_token_obj, docker_client)

    # step 3 - convert the oc template to helm skaffold
    template2helm(result)

    # step 4 - create the helm package
    helm_package('helm_create_package', result, docker_client)

    # step 5 - push the helm package
    # helm_package('helm_push_package', result, docker_client)

main()