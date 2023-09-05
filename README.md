# template2helm-py

> This site was built by the project: [template2helm-py](https://github.com/dedalus-enterprise-architect/template2helm-py)

_template2helm-py_ is a __Pythonic__ utility that help to converts _OpenShift Templates_ into _Helm Charts_ fastest.

A command-line script to run all the steps summarized at _Usage_ paragraph ahead providing the basic information to run each command in the list and letting the script work for you.

The actual configuration will be saved in a __config.json__ file, to allow later connection to work without user input.

The main advantage in using this script is getting started with a very first draft of the Helm Chart starting from an Openshift Template.

## Requirements

It follows the OS tools requirements:

- python 3.5+
- docker 20+
- helm 3+ (optional)

### Project Dependencies

- [template2helm](https://github.com/dedalus-enterprise-architect/template2helm/tree/ea_team_crd) (Dedalus Version)
- [ea-utils image](public.ecr.aws/dedalus-ea/ea-utils:v4-5) as docker image

## Usage

It follow the step list covered by this script:

1. get the aws ecr token

1. get the Openshift Template

1. convert the oc template to an helm base schema

1. create the helm package

1. (disabled feature) push the helm package

### Installation

Install the dependencies with *pip*:

```bash
pip install requirements.txt
```

### Run

```bash
python init.py
```

The script is interactive and will ask you for some information better explained on the next sub paragraph.

### Script Parameters

The initial execution of the script will fill a file named: "*config.json*" with the following keys:

```json
{
    "access_key_id": "",
    "secret_access_key": "",
    "region": "",
    "utility_image": "public.ecr.aws/dedalus-ea/ea-utils:latest",
    "target_image": "",
    "project_root_directory": "/type_here_the_working_dir_full_path/test",
    "src_template_name": "dedalus.template.yml",
    "helm_chart_name": "dedalus-sample-webapp",
    "project_version": "x.y.z",
    "github_pat": "github_pat",
    "confirmation": true
}
```

where if follows the parameters meaning:

- AWS ECR keys:
        **access_key_id**
        **secret_access_key**
        **region**

- __utility_image__ : this is the utility image. [default: *public.ecr.aws/dedalus-ea/ea-utils:latest*]

- __target_image__ : the target image where the Openshift Template is stored in.

- __project_root_directory__ : this is the working dir [i.e. : /opt/projects/folder]

- __src_template_name__ : this is the default Openshift Template Name [default: *dedalus.template.yml*]

- __helm_chart_name__ : this is the folder name where the helm package is being created

- __project_version__ : specify here the helm chart version

- __github_pat__ : this is the *github_pat* as required by the Helm Chart Repository on GitHub (OPTIONAL)
