import copy
import functools
import uuid

from kivy.app import App
from kivy.cache import Cache

from propagation_api.services.project_service import ProjectService
from propagation_api.services.pubsub.pubsub_model import Event, \
    ObservableDaoLinkedEntityList
from propagation_api.utils import setInterval

"""
Context with a possibility to add refresh timeout. After timeout the callback is called that has to update the value in cache.
The Context has to support observer pattern and notify the subscribers after the update.
Also there must be a possibility to FORCE to update the cache thus resetting the timeout timer.
"""
class Context:

    dep_category = "dependencies"
    state_category = "state"

    def __init__(self, name: str = None):
        self.categories = set()
        if name is None:
            name = str(uuid.uuid4())[:8]

        self.name = name
        self.timers = []

    @staticmethod
    def __complete_category_decor(func):
        @functools.wraps(func)
        def wrapper(self, *args, category='default', **kwargs):
            category = f"{self.name}:{category}"
            result = func(self, *args, category=category, **kwargs)
            return result

        return wrapper

    @staticmethod
    def __category_check_decor(func):
        @functools.wraps(func)
        def wrapper(self, *args, category, limit=None, timeout=None, **kwargs):
            if category not in self.categories:
                Cache.register(category, limit, timeout)
                self.categories.add(category)

            result = func(self, *args, category=category, **kwargs)
            return result

        return wrapper

    """
    Arguments limit and timeout will make sense only if category does not yet exist.
    """
    @__complete_category_decor
    @__category_check_decor
    def append_cache(self, key, value, category):
        Cache.append(category, key, value)

    @__complete_category_decor
    @__category_check_decor
    def append_refreshable_cache(self, key, value, category, refresh_after=10.0, refresh_callback=None, subscribers=None):
        Cache.append(category, key, value)

        if refresh_callback is not None:
            self.timers.append(setInterval(refresh_callback, refresh_after, target=value, subscribers=subscribers))

    @__complete_category_decor
    def get(self, key, category, default=None):
        return Cache.get(category, key, default)

    def terminate(self):
        for timer in self.timers:
            timer.cancel()

        self.timers = []


"""
Whenever entity is deleted or added CACHE event is fired
"""
class ProjectCacheState(ObservableDaoLinkedEntityList):

    def __init__(self):
        super().__init__(handlers={
            Event.project_added_event: self.project_added_event_handler,
            Event.project_deleted_event: self.project_deleted_event_handler
        })

    def sync(self):
        self.clear()
        for item in get_project_service().get_all_projects():
            self[item.id] = item

    # TODO: Define handlers
    def project_added_event_handler(self, event: Event, **kwargs):
        project = copy.copy(event.target)
        self.append(project)

    def project_deleted_event_handler(self, event: Event, **kwargs):
        if event.target.id in self:
            del self[event.target.id]


def get_project_service() -> ProjectService:
    return App.get_running_app().context.get('ProjectService', category=Context.dep_category)


def get_projects_state() -> ProjectCacheState:
    return App.get_running_app().context.get('Projects', category=Context.state_category)


# TODO: add to each "with" method decorator that checks for refresh_after and refresh_callback
class ContextBuilder:

    def __init__(self):
        self.currentContext = Context()
        self.currentCategory = 'default'

    def with_category(self, category: str):
        self.currentCategory = category
        return self

    def with_project_service(self, project_service: ProjectService):
        self.currentContext.append_cache('ProjectService', project_service, category=self.currentCategory)
        return self

    def with_projects(self, projects: ProjectCacheState, **kwargs):
        self.currentContext.append_refreshable_cache('Projects', projects, category=self.currentCategory, **kwargs)
        return self

    def build(self):
        ctx = self.currentContext
        self.currentContext = None
        return ctx

    def register_in_app(self):
        App.get_running_app().context = self.currentContext
        ctx = self.currentContext
        self.currentContext = None
        return ctx
