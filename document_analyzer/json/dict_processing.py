def remove_empty_objects(json: dict) -> dict:
    new_json = {}
    for key in json.keys():
        if isinstance(json[key], dict):
            new_json[key] = remove_empty_objects(json[key])
        elif isinstance(json[key], list):
            new_json[key] = remove_empty_objects_from_list(json[key])
        else:
            new_json[key] = json[key]

    return new_json

def remove_empty_objects_from_list(objects: list) -> list:
    new_list = []
    for obj in objects:
        if isinstance(obj, dict):
            if not is_empty_dict(obj):
                new_list.append(obj)
        else:
            new_list.append(obj)

    return new_list

def is_empty_dict(object) -> bool:
    if isinstance(object, dict):
        return all([value == None or value == [] or is_empty_dict(value) for value in object.values()])
    
    return False