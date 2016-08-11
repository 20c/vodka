import handlers
import renderers
import data_types

_handlers = {}


def handle(data_type, data, data_id=None, caller=None):
    """
    execute all data handlers on the specified data according to data type

    Args:
        data_type (str): data type handle
        data (dict or list): data

    Kwargs:
        data_id (str): can be used to differentiate between different data
            sets of the same data type. If not specified will default to
            the data type
        caller (object): if specified, holds the object or function that 
            is trying to handle data

    Returns:
        dict or list - data after handlers have been executed on it
    """

    if not data_id:
        data_id = data_type

    # instantiate handlers for data type if they havent been yet
    if data_id not in _handlers:
        _handlers[data_id] = dict(
            [(h.handle, h) for h in handlers.instantiate_for_data_type(data_type, data_id=data_id)])

    for handler in _handlers[data_id].values():
        data = handler(data, caller=caller)

    return data
