import os
import sys

import contextlib as cl
import pkg_resources


def application_root():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.getcwd()


def application_path(*paths):
    return os.path.join(application_root(), *paths)


def resource_path(package, path, *paths):
    return pkg_resources.resource_filename(package, os.path.join(path, *paths))


@cl.contextmanager
def open_resource(package, resource):
    stream = pkg_resources.resource_stream(package, resource)
    with cl.closing(stream) as file:
        yield file
