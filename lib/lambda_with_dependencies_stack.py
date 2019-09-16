from pathlib import Path
from aws_cdk import (
    aws_lambda as _lambda,
    core,
)
from aws_cdk_lambda_asset.zip_asset_code import ZipAssetCode

class LambdaWithDepStack(core.Stack):
    """Lambda With Dependencies Stack

    This stack packages up a lambda with dependencies.
    """

    def __init__(self, scope: core.App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        work_dir = Path(__file__).parents[1]
        cfn_lambda = _lambda.Function(
            self, 'CFNLambda',
            code=ZipAssetCode(work_dir=f'{work_dir}/lambda', include=['deploy_cfn_lambda'], file_name='cfn-lambda.zip'),
            handler='deploy_cfn_lambda/deploy_cfn_lambda.handler',
            runtime=aws_lambda.Runtime.PYTHON_3_7
        )


    