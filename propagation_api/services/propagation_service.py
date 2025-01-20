import shutil, os
from propagation_api.model.dto.propagation import PropagationDto


class PropagationService:

    def propagate_project(self, propagation: PropagationDto):
        dst = os.path.join(propagation.dst, os.path.basename(propagation.project.path))
        shutil.copytree(propagation.project.path, dst)
