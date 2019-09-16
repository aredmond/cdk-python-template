#!/usr/bin/env python3

from os import environ
from aws_cdk import core

from lib.example_stepfunction_stack import ExampleStepFunctionStack

# Create an environment parameter by pulling relavent env info from system
# variables, set defaults to ensure these variables are set before allowing
# CDK to deploy the stack.
env_west_2 = {
    'account': environ.get('CDK_DEFAULT_ACCOUNT', '111111111111'),
    'region': environ.get('CDK_DEFAULT_REGION','us-west-2') }

app = core.App()
ExampleStepFunctionStack(app, "example-stepfunction-sbx", env=env_west_2)

app.synth()
