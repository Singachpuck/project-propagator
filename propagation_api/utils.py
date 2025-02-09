import threading

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TimerWrapper:

    def __init__(self):
        self.timer = None

    def start(self):
        self.timer.start()

    def cancel(self):
        self.timer.cancel()


def __interval_internal(callback, interval, timerWrapper, *args, **kwargs):
    def wrapper():
        callback(*args, **kwargs)
        __interval_internal(callback, interval, timerWrapper, *args, **kwargs)

    if timerWrapper.timer is not None:
        timerWrapper.cancel()

    timerWrapper.timer = threading.Timer(interval, wrapper)
    timerWrapper.start()


def setInterval(callback, interval, *args, **kwargs):
    timerWrapper = TimerWrapper()

    __interval_internal(callback, interval, timerWrapper, *args, **kwargs)

    return timerWrapper
