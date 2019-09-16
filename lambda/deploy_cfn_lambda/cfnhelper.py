from __future__ import print_function

import yaml
# import pkg_resources
import datetime
import time

def generic_constructor(loader, tag, node):
    classname = node.__class__.__name__
    if (classname == 'SequenceNode'):
        return loader.construct_sequence(node)
    elif (classname == 'MappingNode'):
        return loader.construct_mapping(node)
    else:
        return loader.construct_scalar(node)

yaml.add_multi_constructor('', generic_constructor)

class cfnhelper(object):
    """Create, Update, Delete and more with this cloudformation 
    hepler class

    Attributes:
        boto3_waiter_config: How often and how many times a boto3 
            waiter checks for an operation to complete
        pickle_prefix: Prefix to be added to ssmparam pickle files.
        boto_client: The boto3 client used in the CFN calls
        stack_name: Name of the CFN stack
    """
    boto3_waiter_config={
        'Delay': 5,
        'MaxAttempts': 120
    }

    def __init__(self, boto_client, stack_name):
        """Return a SSMParam object whose boto_client is *boto_client*.""" 
        self.boto_client = boto_client
        self.stack_name = stack_name

    #################################################
    ## Basic Functions
    #################################################
    def list_stacks(self):
        """List CFN Stacks """
        try:
            response =  self.boto_client.list_stacks()
        except Exception as e:
            raise(e)
        return response

    def stack_status(self):
        """Get the current status of a CFN stack """
        try:
            cfn_stack_status = self.boto_client.describe_stacks(StackName=self.stack_name).get('Stacks')[0].get('StackStatus')
        except Exception as e:
            # if 'AlreadyExistsException' not in str(e):
            #     raise(e)
            # print('Stack', self.stack_name, " exists, skipping creation.")
            # return False
            if 'Stack with id' not in str(e) and 'does not exist' not in str(e):
                raise(e)
            print('Stack', self.stack_name, 'dose not exist.')
            return None
        return cfn_stack_status

    def bootstrap_cfn_stack(self, template_file, param_dict, description='No description'):
        """Create an empty stack then apply a change set. """
        if not self.create_empty_cfn_stack(): return None
        response = self.update_with_change_set(template_file, param_dict, description=description)
        return response

    def create_empty_cfn_stack(self):
        # bootstrap_template = pkg_resources.resource_string(__name__, 'CFNBootStrap.yaml').decode("utf-8")
        with open('CFNBootStrap.yaml') as yaml_data:
            template_body = yaml.load(yaml_data)
        try:
            response = self.boto_client.create_stack(
                StackName=self.stack_name,
                TemplateBody=template_body,
                # Capabilities=['CAPABILITY_IAM'],
                OnFailure='DELETE',
            )
            print(response)
            waiter = self.boto_client.get_waiter('stack_create_complete')
            print("Waiting for cloudformation stack", self.stack_name, "to complete.")
            waiter.wait(StackName=self.stack_name, WaiterConfig=self.boto3_waiter_config)
            print("Creation complete for cloudformation stack", self.stack_name, ".")
        except Exception as e:
            if 'AlreadyExistsException' not in str(e):
                raise(e)
            print('Stack', self.stack_name, "exists, skipping creation.")
            return False
        return response

    def create_change_set(self, template_file, param_dict, description='No description'):
        """Create a CFN change set """
        # template_body = yaml.dump(bootstrap_template)
        # print(template_body)
        # with open('lib/cfn/CFNBootStrap.yaml') as yaml_data:
        #     template_data = yaml.load(yaml_data)
        #     template_body = yaml.dump(template_data)
        with open(template_file, "r") as in_fh:
            # Read the file into memory as a string so that we can try
            # parsing it twice without seeking back to the beginning and
            # re-reading.
            template_body = in_fh.read()

        ts = time.time()
        time_stamp_str = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
        change_set_name = self.stack_name + '-' + time_stamp_str
        print(change_set_name)
        print(param_dict)
        try:
            response = self.boto_client.create_change_set(
                StackName=self.stack_name,
                TemplateBody=template_body,
                Parameters=param_dict,
                Capabilities=['CAPABILITY_IAM'],
                # Tags=[
                #     {
                #         'Key': 'nse:app:costcenter',
                #         'Value': '1234'
                #     },
                # ],
                ChangeSetName=change_set_name,
                Description=description,
                # ChangeSetType='CREATE'|'UPDATE'
            )
            print(response)
            waiter = self.boto_client.get_waiter('change_set_create_complete')
            print("Waiting for cloudformation change set", change_set_name, "creation to complete.")
            waiter.wait(ChangeSetName=change_set_name, StackName=self.stack_name, WaiterConfig=self.boto3_waiter_config)
            print("Creation complete for cloudformation change set", change_set_name, ".")
        except Exception as e:
            ## Determine if the issue was caused by a no change error and delete the change set if it was.
            if 'Waiter ChangeSetCreateComplete failed:' not in str(e):
                raise(e)
            change_set_failure_reason = self.boto_client.describe_change_set(ChangeSetName=change_set_name, StackName=self.stack_name).get('StatusReason')
            if "didn't contain changes." not in change_set_failure_reason:
                raise Exception(change_set_failure_reason)
            print("No Changes to be made.")
            self.delete_change_set(change_set_name)
            return False
            
        return change_set_name

    def execute_change_set(self, change_set_name):
        try:
            response = self.boto_client.execute_change_set(
                ChangeSetName=change_set_name,
                StackName=self.stack_name
            )
            print(response)
            waiter = self.boto_client.get_waiter('stack_update_complete')
            print("Waiting for cloudformation change set", change_set_name, "execution to complete.")
            waiter.wait(StackName=self.stack_name, WaiterConfig=self.boto3_waiter_config)
            print("Execution complete for cloudformation change set", change_set_name, ".")
        except Exception as e:
            raise(e)
        return response

    def delete_change_set(self, change_set_name):
        print('Deleting change set', change_set_name)
        try:
            response = self.boto_client.delete_change_set(
                ChangeSetName=change_set_name,
                StackName=self.stack_name
            )
            print(response)
        except Exception as e:
            raise(e)
        return response

    def delete_cfn_stack(self):
        try:
            response = self.boto_client.delete_stack(StackName=self.stack_name)
            print(response)
            waiter = self.boto_client.get_waiter('stack_delete_complete')
            print("Waiting for cloudformation stack", self.stack_name, "to delete.")
            waiter.wait(StackName=self.stack_name)
            print("Deletion complete for cloudformation stack", self.stack_name, ".")
        except Exception as e:
            raise(e)
        return response

    #################################################
    ## Helper Functions
    #################################################
    def update_with_change_set(self, template_file, param_dict, description='No description'):
        change_set_name = self.create_change_set(template_file, param_dict, description=description)
        ## If there is no change, don't try and execute.
        if not change_set_name: return False
        response = self.execute_change_set(change_set_name)
        return response
