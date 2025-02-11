from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from propagation_api.dao.project_dao import InMemoryProjectDao
from propagation_api.model.dto.propagation import PropagationDto
from propagation_api.model.entity.project import Project
from propagation_api.services import context
from propagation_api.services.context import ProjectCacheState, Context
from propagation_api.services.project_service import ProjectService
from propagation_api.services.propagation_service import PropagationService
from propagation_api.services.pubsub.pubsub_model import Subscriber, Event


class FileBrowser(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def file_path(self):
        for child in self.children:
            if isinstance(child, TextInput):
                return child

    @property
    def text(self):
        return self.file_path.text

    def select_file(self):
        from plyer import filechooser
        filechooser.choose_dir(on_selection=self.selected)

    def selected(self, selected):
        if len(selected) > 0:
            self.file_path.text = selected[0]


class MainMenu(Screen):
    pass


class PropagateProjectScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.propagation_service = context.get_propagation_service()

    # TODO: Propagation
    def propagate_clicked(self):
        propagation = PropagationDto()
        self.propagation_service.propagate_project()
        pass

    def cancel(self):
        self.manager.current = "main_menu"


class ConfigureProjectsScreen(Screen):

    def add_project_clicked(self):
        add_project_modal = AddProjectModal(self.ids.inputProjectDir.text)
        add_project_modal.open()

    def cancel(self):
        self.manager.current = "main_menu"


class ProjectList(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.data = []

        self.updater = ProjectListUpdater(self)
        self.updater.refresh()


class ProjectListUpdater(Subscriber):

    def __init__(self, project_list):
        super().__init__(handlers={
            Event.cache_cleared: self.reset,
            Event.cache_added_event: self.add_to_list,
            Event.cache_deleted_event: self.delete_from_list
        })

        self.project_list = project_list

        self.project_service = context.get_project_service()
        self.projects_state = context.get_projects_state()
        self.projects_state.subscribe(self)

        self.refresh()

    def reset(self):
        self.project_list.data.clear()

    def refresh(self):
        self.project_list.data = [{
            "id": item_id,
            "text": f"{item.name} - {item.path}"}
            for item_id, item in self.projects_state.items()
        ]

    def add_to_list(self, event, **kwargs):
        project = kwargs["entity"]
        self.project_list.data.append({
            "id": project.id,
            "text": f"{project.name} - {project.path}"
        })

    def delete_from_list(self, event, **kwargs):
        project_id = kwargs["entity_id"]

        for i in range(0, len(self.project_list.data)):
            if project_id == self.project_list.data[i]["id"]:
                del self.project_list.data[i]
                break


class AddProjectModal(ModalView):

    def __init__(self, projectPathBind: str, **kwargs):
        super().__init__(**kwargs)
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
        propagation_service = PropagationService()

        projects_state = ProjectCacheState()

        context.ContextBuilder() \
            .with_category(Context.dep_category) \
            .with_project_service(project_service) \
            .with_propagation_service(propagation_service) \
            .with_category(Context.state_category) \
            .with_projects(projects_state, refresh_callback=lambda **kwargs: print("Ping!"), refresh_after=3) \
            .register_in_app()

        projects_state.sync()
        project_service.dao_state_pub.subscribe(projects_state)

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
