import handlers
import renderers
import data_types

_handlers = {}


def handle(data_type, data, data_id=None, caller=None):
    if not data_id:
        data_id = data_type

    # instantiate handlers for data type if they havent been yet
    if data_id not in _handlers:
        _handlers[data_id] = dict(
            [(h.handle, h) for h in handlers.instantiate_for_data_type(data_type, data_id=data_id)])

    for handler in _handlers[data_id].values():
        data = handler(data, caller=caller)

    return data
