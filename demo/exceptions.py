# -*- coding: utf-8 -*-

"""This module contains exceptions for Demo."""

# For py2.7 compatibility
from __future__ import print_function

import functools
import inspect


class DemoException(Exception):
    """Base exception for any error raised in a Demo.

    Initializing an instance of DemoException with some text will override the default text defined in the class.
    
    Attributes:
        text (str): The text to print when an instance is caught.
    """
    text = None
    def __init__(self, text=None):
        """Override the default class text if `text` is given.

        Args:
            text (str, optional): A custom error text.
        """
        if text:
            self.text = text


class DemoRestart(DemoException):
    """Raised when user restarts a demo."""
    text = "Restarting."


class DemoExit(DemoException):
    """Raised when user quits a demo."""
    text = "Goodbye!"


class DemoRetry(DemoException):
    """Raised when an input function should be called again."""
    text = ""


class OptionError(DemoException):
    """Base exception for any error raised when an option is selected.

    Instances of OptionError must be initialized with an option. It will be used to format the class format string.
    
    Attributes:
        text (str): A format string for an option.
    """
    def __init__(self, option):
        """Format the class text with an option name.
        
        Args:
            option (str): The option name.
        """
        self.text = self.text.format(option)


class KeyNotFoundError(OptionError):
    """Raised when a key does not exist in the options cache."""
    text = "'{}' does not exist in the cache."


class OptionNotFoundError(OptionError):
    """Raised when an option is not registered."""
    text = "'{}' not registered."


class CallbackNotFoundError(OptionError):
    """Raised when an option has no callback."""
    text = "'{}' callback not registered"


class CallbackNotLockError(OptionError):
    """Raised when a callback for an option was flagged as a lock but does not accept a `key` argument."""
    text = "'{}' callback not lock, key rejected"


def catch_exc(*demo_exc):
    """Catch instances of `demo_exc` raised while running a function.

    Args:
        *demo_exc: One or a few subclasses of DemoException, and possibly a function to wrap.

    Returns:
        catch_exc_decorator: A decorator that takes a function and returns a wrapped function. As a shortcut, if a function was passed into `demo_exc`, the wrapped function is returned instead.
    
    Note:
        * Non-subclasses of DemoException are ignored, unless a function or method is provided. 

        * DemoException is the default if no subclasses are provided.
    
        * If a KeyboardInterrupt is raised, it will be re-raised as DemoExit.

        * Non-instances of `demo_exc` will not be caught. They should typically be handled by a higher level and more general kind of catch_exc.
    """
    func = None
    demo_exc = list(demo_exc)
    for i in range(len(demo_exc)-1, -1, -1):
        try:
            if not issubclass(demo_exc[i], DemoException):
                demo_exc.pop(i)
        except TypeError:
            obj = demo_exc.pop(i)
            if (inspect.isfunction(obj) or inspect.ismethod(obj)) and not func:
                func = obj
    if demo_exc:
        demo_exc = tuple(demo_exc)
    else:
        demo_exc = DemoException
    def catch_exc_decorator(func):
        @functools.wraps(func)
        def inner(demo, *args, **kwargs):
            while True:
                try:
                    try:
                        return func(demo, *args, **kwargs)
                    except KeyboardInterrupt:
                        print()
                        demo.quit()
                except demo_exc as exc:
                    if exc.text:
                        print(exc.text)
                        print()
                    if isinstance(exc, DemoExit):
                        break
        return inner
    if func:
        return catch_exc_decorator(func)
    else:
        return catch_exc_decorator

