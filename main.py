from os.path import isdir, join

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.modalview import ModalView
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from propagation_api.dao.project_dao import ORMProjectDao, InMemoryProjectDao
from propagation_api.model.entity.project import Project
from propagation_api.services import context
from propagation_api.services.project_service import ProjectService
from propagation_api.utils import Base


class MainMenu(Screen):
    pass


class PropagateProjectScreen(Screen):
    pass


class ConfigureProjectsScreen(Screen):
    # def is_dir(self, directory, filename):
    #     return isdir(join(directory, filename))

    def select_file(self):
        from plyer import filechooser
        filechooser.choose_dir(on_selection=self.selected)

    def selected(self, selected):
        if len(selected) > 0:
            self.ids.inputProjectDir.text = selected[0]

    def add_project_clicked(self):
        add_project_modal = AddProjectModal(self.ids.inputProjectDir.text)
        add_project_modal.open()

        add_project_modal.bind(on_pre_dismiss=lambda _: self.ids.projectList.refresh())


class ProjectList(RecycleView):
    def __init__(self, **kwargs):
        super(ProjectList, self).__init__(**kwargs)
        self.project_service = context.get_project_service()
        self.data = []
        self.refresh()

    def refresh(self):
        self.data = [{'text': f"{item.name} - {item.path}"} for item in self.project_service.get_all_projects()]


class AddProjectModal(ModalView):

    def __init__(self, projectPathBind: str, **kwargs):
        super().__init__(**kwargs)
        # self.projectPathBind = projectPath
        self.ids.projectPath.text = projectPathBind

    def add_project_clicked(self):
        project = Project()
        project.name = self.ids.projectName.text
        project.path = self.ids.projectPath.text

        context.get_project_service().add_project(project)

        self.dismiss()


class ProjectPropagatorApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = None

    def build(self):
        # engine = create_engine("sqlite:///example.db")
        # Base.metadata.create_all(engine)

        # project_dao = ORMProjectDao(engine)
        project_dao = InMemoryProjectDao()
        project_service = ProjectService(project_dao)

        # ctx['ProjectService'] = project_service

        # self.context['ProjectService'] = project_service
        ctx = context.ContextBuilder() \
            .with_category("dependencies") \
            .with_project_service(project_service) \
            .with_category("state") \
            .with_projects([], refresh_callback=lambda **kwargs: print("Ping!"), refresh_after=3) \
            .register_in_app()

        # ctx.append_refreshable_cache("ping", [], category='test', refresh_after=3,
        #                           refresh_callback=lambda **kwargs: print("Ping!"))
        # ctx.append_refreshable_cache("ping", [], category='test', refresh_after=2,
        #                           refresh_callback=lambda **kwargs: print("Ping2!"))

        # Create the screen manager
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MainMenu(name='main_menu'))
        sm.add_widget(PropagateProjectScreen(name='propagate_project'))
        sm.add_widget(ConfigureProjectsScreen(name='configure_projects'))

        return sm

    def on_stop(self):
        self.context.terminate()


if __name__ == '__main__':
    # Create a session factory
    # Session = sessionmaker(bind=engine)
    # session = Session()
    Builder.load_file('layout/project_propagator.kv')
    ProjectPropagatorApp().run()
