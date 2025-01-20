from propagation_api.model.entity.project import Project


class PropagationDto:

    def __init__(self, project: Project, dst: str):
        self.project = project
        self.dst = dst
