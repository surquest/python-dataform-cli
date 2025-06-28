import os
from google.cloud import dataform_v1
from google.api_core import exceptions

class DataformHandler:

    dataform_client = dataform_v1.DataformClient()

    def __init__(self, dataform_client, gitignore_file):
        
        self.dataform_client = dataform_client
        self.gitignore_file = gitignore_file

    @classmethod
    def get_workspace_path(cls, project_id, region, repository_id, workspace_id):

        return cls.dataform_client.workspace_path(
            project_id, 
            region,
            repository_id,
            workspace_id
        )