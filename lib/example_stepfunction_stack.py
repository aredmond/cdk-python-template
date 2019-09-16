from aws_cdk import (
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
    aws_lambda as _lambda,
    core,
)
import json

class ExampleStepFunctionStack(core.Stack):
    """Example Step Function CDK Stack

    This stack creates a stepfunction that loops 3 times and then completes,
    it expects a `wait_time` parameter in the execution json for the 
    stepfunction.  Set this low enough so the stepfunction does not time out.
    """

    def __init__(self, scope: core.App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        pass_through_lambda = _lambda.Function(
            self, 'PassThroughLambda',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('lambda'),
            handler='pass_through_lambda.handler'
        )

        loop_count_lambda = _lambda.Function(
            self, 'LoopCountLambda',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.asset('lambda'),
            handler='loop_count_lambda.handler'
        )

        start_state_machine = sfn.Task(
            self, "Start CodeBuild Lambda",
            task=sfn_tasks.InvokeFunction(pass_through_lambda)
        )

        wait_x = sfn.Wait(
            self, "Wait X Seconds",
            time=sfn.WaitTime.seconds_path('$.wait_time'),
        )

        get_state_machine_status = sfn.Task(
            self, "Get Build Status",
            task=sfn_tasks.InvokeFunction(loop_count_lambda)
        )

        is_complete = sfn.Choice(
            self, "Job Complete?"
        )

        state_machine_failed = sfn.Fail(
            self, "Build Failed",
            cause="AWS Batch Job Failed",
            error="DescribeJob returned FAILED"
        )

        state_machine_success = sfn.Pass(
            self, "Build Successs"
        )

        definition = start_state_machine\
            .next(wait_x)\
            .next(get_state_machine_status)\
            .next(is_complete
                  .when(sfn.Condition.string_equals(
                      "$.status", "FAILED"), state_machine_failed)
                  .when(sfn.Condition.string_equals(
                      "$.status", "SUCCEEDED"), state_machine_success)
                  .otherwise(wait_x))

        sfn.StateMachine(
            self, "StateMachine",
            definition=definition,
            timeout=core.Duration.seconds(60),
        )
