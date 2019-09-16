from aws_cdk import (
    # aws_lambda as _lambda,
    core,
)

class EmptyStack(core.Stack):
    """Empty App Stack

    Copy this file to save some typing
    """

    def __init__(self, scope: core.App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)