from projects.models import ProjectDb
from projects.read_write_project import read_project


class FedsGenerator:

    def __init__(self, project_id):
        self.project_id = project_id
        self.project_db = ProjectDb.objects.get(pk=project_id)
        self.project = read_project(project_id)
        # Create valid customer table.
        cust_table_name = create_valid_customer_table()

