from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
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

        self._propagation_service = context.get_propagation_service()
        self._project_state = context.get_projects_state()
        self._project_list_w = self.ids.projectList
        self._prop_path_w = self.ids.propagatePath

    def propagate_clicked(self):
        p_id = self._project_list_w.get_selected_project_id()
        selected_project = self._project_state[p_id] if p_id in self._project_state else None
        if selected_project is not None and len(self._prop_path_w.text) > 0:
            propagation = PropagationDto(project=selected_project, dst=self._prop_path_w.text)
            self._propagation_service.propagate_project(propagation)

    def cancel(self):
        self.manager.current = "main_menu"


class ConfigureProjectsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        self._project_service = context.get_project_service()
        self._project_list_w = self.ids.projectList

    def add_project_clicked(self):
        add_project_modal = AddProjectModal(self.ids.inputProjectDir.text)
        add_project_modal.open()

    # TODO
    def modify_project_clicked(self):
        pass

    def delete_project_clicked(self):
        p_id = self._project_list_w.get_selected_project_id()
        if p_id is not None:
            self._project_service.delete_project_by_id(p_id)

    def cancel(self):
        self.manager.current = "main_menu"


# class ProjectList(RecycleView):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         self.data = []
#
#         self.updater = ProjectListUpdater(self)
#         self.updater.refresh()
#
#     def supply_item(self, project):
#         return {
#             "id": project.id,
#             "text": f"{project.name} - {project.path}"
#         }

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
        self.project_list.data = [
            self.project_list.supply_item(project)
            for project_id, project in self.projects_state.items()
        ]

    def add_to_list(self, event, **kwargs):
        project = kwargs["entity"]
        self.project_list.data.append(self.project_list.supply_item(project))

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

class SelectableProjectList(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.data = []
        self._project_service = context.get_project_service()

        self.updater = ProjectListUpdater(self)
        self.updater.refresh()

    def supply_item(self, project):
        return {
            "id": project.id,
            "text": f"{project.name} - {project.path}"
        }

    def get_selected_project_id(self) -> int | None:
        child = next(filter(lambda ch: isinstance(ch, SelectableLabel) and ch.selected, self.ids.listLayout.children), None)
        if child is None:
            return None

        return child.id

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behavior to the view. '''
    pass


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))

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
        project_service._dao_state_pub.subscribe(projects_state)

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
