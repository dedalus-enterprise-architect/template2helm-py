# template2helm-py

template2helm-py is a Pythonic utility that help to converts OpenShift templates into Helm charts faster.

A command-line script to login to an EKS cluster providing the basic information to connect and letting the script work for you. The actual configuration will be saved in a *config.json* file, to allow later connection to work without user input.

## Requirements

It follows the OS tools requirements:

- python 3.5+
- docker 20+
- helm 3+

## Installation

Install the dependencies with *pip*:

```bash
pip install requirements.txt
```

Run the script:

```bash
python init.py
```

## Script Parameters

The initial execution of the script will fill a file named: "*config.json*" with the following keys:

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

where if follows the parameters meaning:

- AWS ECR keys:
        **access_key_id**
        **secret_access_key**
        **region**
- **utility_image** : this is the utility image. [default: *public.ecr.aws/dedalus-ea/ea-utils:latest*]
- **target_image** : the target image where the Openshift Template is stored in.
- **project_root_directory** : this is the working dir [i.e. : /opt/projects/folder]
- **src_template_name** : this is the default Openshift Template Name [default: *dedalus.template.yml*]
- **helm_chart_name** : this is the folder name where the helm package is being created
- **project_version** : specify here the helm chart version
- **github_pat** : this is the *github_pat* as required by the Helm Chart Repository on GitHub (OPTIONAL)
