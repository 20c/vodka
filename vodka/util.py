def dict_get_path(data, path, default=None):
    """
    Returns the value inside nested structure of data located
    at period delimited path
    
    When traversing a list, as long as that list is containing objects of 
    type dict, items in that list will have their "name" and "type" values 
    tested against the current key in the path.

    Args:
        data (dict or list): data to traverse
        path (str): '.' delimited string
    
    Kwargs:
        default: value to return if path does not exist
    """

    keys = path.split(".") 
    for k in keys:
        if type(data) == list:
            found = False
            for item in data:
                name = item.get("name", item.get("type"))
                if name == k:
                    found = True
                    data = item
                    break
            if not found:
                return default
        elif type(data) == dict:
            if k in data:
                data = data[k]
            else:
                return default
        else:
            return default
    return data 
