import pkgutil
import warnings
import importlib
import inspect
import sys
import time
import logging

from .base import Plugin
logger = logging.getLogger('intake')


def autodiscover(path=None, plugin_prefix='intake_'):
    """Scan for Intake plugin packages and return a dict of plugins.

    This function searches path (or sys.path) for packages with names that
    start with plugin_prefix.  Those modules will be imported and scanned for
    subclasses of intake.source.base.Plugin.  Any subclasses found will be
    instantiated and returned in a dictionary, with the plugin's name attribute
    as the key.
    """

    plugins = {}

    for importer, name, ispkg in pkgutil.iter_modules(path=path):
        if name.startswith(plugin_prefix):
            t = time.time()
            new_plugins = load_plugins_from_module(name)

            for plugin_name, plugin in new_plugins.items():
                if plugin_name in plugins:
                    orig_path = inspect.getfile(plugins[plugin_name].__class__)
                    new_path = inspect.getfile(plugin.__class__)
                    warnings.warn('Plugin name collision for "%s" from'
                                  '\n    %s'
                                  '\nand'
                                  '\n    %s'
                                  '\nKeeping plugin from first location.'
                                  % (plugin_name, orig_path, new_path))
                else:
                    plugins[plugin_name] = plugin
            logger.debug("Import %s took: %7.2f s" % (name, time.time() - t))

    return plugins


def load_plugins_from_module(module_name):
    """Imports a module and returns dictionary of discovered Intake plugins.

    Plugin classes are instantiated and added to the dictionary, keyed by the
    name attribute of the plugin object.
    """
    plugins = {}

    mod = importlib.import_module(module_name)
    for _, cls in inspect.getmembers(mod, inspect.isclass):
        # Don't try to register plugins imported into this module elsewhere
        if issubclass(cls, Plugin) and cls.__module__ == module_name:
            plugin = cls()
            plugins[plugin.name] = plugin

    return plugins
