from propagation_api.model.dto.propagation import PropagationDto
from propagation_api.model.entity.project import Project
from propagation_api.services.propagation_service import PropagationService


def test_propagate():
    service = PropagationService()

    project = Project(name="Project 1", path="D:\projects\project-propagator\\tests\dummy\projects\project1")

    prop = PropagationDto(project=project, dst="D:\projects\project-propagator\\tests\dummy\\bucket")

    service.propagate_project(prop)
