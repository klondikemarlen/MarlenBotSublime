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


def flatten(data):
    flatter_data = OrderedDict()

    try:
        for outer_key, outer_value in data.items():
            for inner_key, inner_value in outer_value.items():
                flatter_data['.'.join([outer_key, inner_key])] = inner_value
        return flatten(flatter_data)
    except AttributeError:
        return data


class YamlPath(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()

        # Gross simplification, sel() returns a bunch of regions
        # regions have start and end points.
        # Essentially we only care about the first one.
        regions = self.view.sel()
        cursor_position = regions[0].begin()

        data = None
        with open(file_name) as f:
            try:
                data = ordered_load(f.read(cursor_position))
            except yaml.parser.ParserError:
                sublime.status_message("Failed to parse YAML file.")

        key_at_cursor, value_at_cursor = flatten(data).popitem()
        sublime.set_clipboard(key_at_cursor)
        sublime.status_message("Path is '{}' (value {}), copied to clipboard.".format(key_at_cursor, repr(value_at_cursor)))
