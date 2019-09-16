# Python Template for CDK

This template has an alternative `setuptools` file structure from the included sample-app template included with CDK. It also has a more comprehensive .gitignore and includes a stepfunction sample stack. The plan is to expand this repo with more sample stacks as time goes one. 

The main drive in creating this template was to speed up my personal development with CDK. This repo represents my personal preference and is not meant as a best practice CDK example.

## Getting started

Make sure to create a python virtual environment and activate that environment before installing the application:  
```
python3 -m venv .env
source .env/bin/activate
```  

Finally, install the local app with the editable flag:  
```
pip install -e .
```

## Using the correct account and region

First set your default AWS profile in the terminal you will run cdk in:  
```
export AWS_PROFILE='my_aws_cli_profile
```  

You will also want to set the default account and region for CDK as a secondary guard rail:  
```
export CDK_DEFAULT_ACCOUNT='111111111111'
export CDK_DEFAULT_REGION='us-west-2'
```

## Add another CDK lib to the application

In the `setup.py` file within the parameters of the call to `setuptools.setup()` function add your CDK components to the `install_requires` parameter. For instance, if you wanted to add IAM support your would change:  
```
install_requires=[
        "aws-cdk.core",
        "aws-cdk.aws-stepfunctions",
        "aws-cdk.aws-stepfunctions-tasks",
        "aws-cdk.aws-lambda"
    ],
```  

To:  
```
install_requires=[
        "aws-cdk.core",
        "aws-cdk.aws-stepfunctions",
        "aws-cdk.aws-stepfunctions-tasks",
        "aws-cdk.aws-lambda",
        "aws-cdk.aws-iam",
    ],
```  

Then reinstall the app to apply the change:  
```
pip install -e .
```  

Avoid installing directly with pip to keep your app code functional for new developers in the future.

### TODO Add checklist of items to rename/change when using this template. ie. stacknames, environment names
