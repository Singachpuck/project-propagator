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
    def getAll(self) -> list[Project]:
        pass

    @abstractmethod
    def getById(self, project_id: int):
        pass

    # @abstractmethod
    # def refresh(self, projects: list[Project]):
    #     pass


class InMemoryProjectDao(ProjectDao):

    def __init__(self):
        self.projects = []
        self.id_sequence = 2

        # Define a base class
        project = Project(id=0, name="Project 1",
                          path="D:\\projects\\project-propagator\\tests\\dummy\\projects\\project1")
        project2 = Project(id=1, name="Project 2",
                           path="D:\\projects\\project-propagator\\tests\\dummy\\projects\\project1")
        self.projects.append(project)
        self.projects.append(project2)

    def create(self, project: Project):
        project.id = self.id_sequence
        self.projects.append(project)
        self.id_sequence += 1
        # TODO: return id
        return project.id

    def remove(self, project):
        self.projects.remove(project)
        return True

    def removeById(self, project_id: int):
        p = self.getById(project_id)
        if p is not None:
            self.remove(p)

    def getAll(self):
        return self.projects

    def getById(self, project_id: int):
        return next((item for item in self.projects if item.id == project_id), None)

    # def refresh(self, projects: list[Project]):
    #     if len(self.projects)


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
        session.close()
        return True if result > 0 else False

    def getAll(self):
        session = self.Session()
        result = session.query(Project).all()
        session.close()
        return result

    def getById(self, project_id: int):
        session = self.Session()
        entity = session.get(Project, project_id)
        session.close()
        return entity
