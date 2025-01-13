from kivy.app import App, Builder
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from utils import Base


class MainMenu(Screen):
    pass


class PropagateProjectScreen(Screen):
    pass


class ConfigureProjectsScreen(Screen):
    pass


class ProjectPropagatorApp(App):
    def build(self):
        # Create the screen manager
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MainMenu(name='main_menu'))
        sm.add_widget(PropagateProjectScreen(name='propagate_project'))
        sm.add_widget(ConfigureProjectsScreen(name='configure_projects'))

        return sm


if __name__ == '__main__':
    engine = create_engine("sqlite:///example.db")
    # Define a base class

    Base.metadata.create_all(engine)
    # Create a session factory
    Session = sessionmaker(bind=engine)
    session = Session()
    # Builder.load_file('layout/project_propagator.kv')
    # ProjectPropagatorApp().run()
