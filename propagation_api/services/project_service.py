from propagation_api.dao.project_dao import ProjectDao
from propagation_api.model.entity.project import Project
from propagation_api.services.pubsub.pubsub_model import Publisher, Event


class ProjectService:

    def __init__(self, project_dao: ProjectDao):
        self.project_dao = project_dao
        self.dao_state_pub = Publisher()

    def add_project(self, project: Project):
        new_id = self.project_dao.create(project)
        project.id = new_id

        event = Event(name=Event.project_added_event, target=project)
        self.dao_state_pub.publish(event)

    def get_all_projects(self):
        return self.project_dao.getAll()

    # TODO: Make flexible project refresh
    def refresh_projects(self):
        pass

    def delete_project_by_id(self, project_id: int):
        to_remove = Project(id=project_id)
        self.project_dao.removeById(project_id=project_id)

        event = Event(name=Event.project_deleted_event, target=to_remove)
        self.dao_state_pub.publish(event)
