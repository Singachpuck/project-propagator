from abc import ABC
from typing import Any

# TODO: Unit test
class Event:

    project_added_event = "PROJECT_ADDED"
    project_deleted_event = "PROJECT_DELETED"

    cache_added_event = "CACHE_ADDED_ENTITY"
    cache_deleted_event = "CACHE_DELETED_ENTITY"
    cache_cleared = "CACHE_CLEARED"

    def __init__(self, name: str, target):
        self.name = name
        self.target = target


class Subscriber:

    def __init__(self, handlers: dict[str, Any]):
        self.handlers = handlers

    def react(self, event: Event, **kwargs):
        if event.name in self.handlers:
            self.handlers[event.name](event, **kwargs)


class Publisher:

    def __init__(self):
        self.subscribers = []

    def subscribe(self, subscriber: Subscriber):
        self.subscribers.append(subscriber)

    def publish(self, event: Event, **kwargs):
        for sub in self.subscribers:
            sub.react(event, **kwargs)


class ObservableItem(Publisher):
    def __init__(self):
        super().__init__()

    def trigger_event(self, event_name: str, **kwargs):
        event = Event(name=event_name, target=self)

        self.publish(event, **kwargs)


class ObservableDaoLinkedEntityList(dict, ObservableItem, Subscriber):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ObservableItem.__init__(self)
        Subscriber.__init__(self, kwargs["handlers"])

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

        self.trigger_event(Event.cache_added_event, entity=value)

    def __delitem__(self, key):
        super().__delitem__(key)

        self.trigger_event(Event.cache_deleted_event, entity_id=key)

    def clear(self):
        super().clear()

        self.trigger_event(Event.cache_cleared)

    def append(self, value):
        self[value.id] = value
