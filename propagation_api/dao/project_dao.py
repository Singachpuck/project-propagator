from abc import ABC, abstractmethod

from sqlalchemy.orm import sessionmaker

from propagation_api.model.entity.project import Project


class ProjectDao(ABC):

    @abstractmethod
    def create(self, project: Project):
        pass

    @abstractmethod
    def remove(self, project: Project):
        pass

    @abstractmethod
    def removeById(self, project_id: int):
        pass

    @abstractmethod
    def getById(self, project_id: int):
        pass


class ORMProjectDao(ProjectDao):

    def __init__(self, engine):
        self.Session = sessionmaker(bind=engine)

    def create(self, project: Project):
        session = self.Session()
        session.add(project)
        session.commit()
        session.close()
        # TODO: return id

    def remove(self, project):
        session = self.Session()
        session.delete(project)
        session.commit()
        session.close()
        return True

    def removeById(self, project_id: int):
        session = self.Session()
        result = session.query(Project).filter_by(id=project_id).delete()
        session.commit()
        return True if result > 0 else False

    def getById(self, project_id: int):
        session = self.Session()
        entity = session.get(Project, project_id)
        session.close()
        return entity
