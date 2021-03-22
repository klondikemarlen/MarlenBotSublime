from collections import OrderedDict

import sublime
import sublime_plugin
import yaml


# from https://stackoverflow.com/a/21912744
def ordered_load(stream, Loader=yaml.SafeLoader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


# From https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys
def flatten(data, parent_key='', sep='.'):
    items = []
    for k, v in data.items():
        new_key = parent_key + sep + str(k) if parent_key else str(k)
        try:
            items.extend(flatten(v, new_key, sep=sep).items())
        except AttributeError:
            items.append((new_key, v))
    return OrderedDict(items)


class YamlPath(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()

        # Gross simplification, sel() returns a bunch of regions
        # regions have start and end points.
        # Essentially we only care about the first one.
        regions = self.view.sel()
        line_at_cursor = self.view.line(regions[0])
        end_of_line = line_at_cursor.end()

        data = None
        with open(file_name, encoding="utf-8") as f:
            try:
                data = ordered_load(f.read(end_of_line))
            except yaml.parser.ParserError:
                sublime.status_message("Failed to parse YAML file.")

        key_at_cursor, value_at_cursor = flatten(data).popitem()
        sublime.set_clipboard(key_at_cursor)
        sublime.status_message("Path is '{}' ({}), copied to clipboard.".format(key_at_cursor, repr(value_at_cursor)))
