from sqlalchemy import create_engine

from propagation_api.dao.project_dao import ProjectDao
from propagation_api.model.entity.project import Project
from propagation_api.utils import Base

engine = create_engine("sqlite:///test.db")

Base.metadata.create_all(engine)


def testCreate():
    dao = ProjectDao(engine)

    project = Project(id=1, name="Project 1", path="path/to/project")
    dao.create(project)

    project2 = dao.getById(1)

    dao.remove(project2)
