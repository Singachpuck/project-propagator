from propagation_api.dao.project_dao import ProjectDao
from propagation_api.model.entity.project import Project


class ProjectService:

    def __init__(self, project_dao: ProjectDao):
        self.project_dao = project_dao

    def add_project(self, project: Project):
        self.project_dao.create(project)
