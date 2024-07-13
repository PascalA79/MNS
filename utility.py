import importlib.util
import re
import secrets
from datetime import datetime
from collections import defaultdict
from threading import Thread
from queue import Queue
from time import sleep
import asyncio
import inspect


def to_camel_case(pascal_case : str):
    new_str = ''
    for num, char in enumerate(pascal_case):
        new_str += '_' + char.lower() if char.isupper() and num!= 0 else char.lower()
    return new_str 

def to_pascal_case(camel_case : str):
    new_str = ''
    last_str = None
    for num, char in enumerate(camel_case):
        if char != '_':
            new_str += char.upper() if last_str == '_' or num == 0  else char.lower()
        last_str = char
    return new_str 

def load_class_from_file(file_path, class_name):
    spec = importlib.util.spec_from_file_location(class_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    loaded_class = getattr(module, class_name)
    return loaded_class

def str_to_integer(string_to_convert : str):
    try:
        if re.fullmatch('[0-9]*',str(string_to_convert)):
            return int(string_to_convert)
    except ValueError:
        return None
    return None

def convert_to_int_if_possible(string_to_convert : str):
    try:
        if re.fullmatch('[0-9]*',str(string_to_convert)):
            return int(string_to_convert)
    except ValueError:
        return None
    return string_to_convert


def is_valid_uuid(value):
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, str(value)))


def subtract_datetime(datetime1, datetime2):
    """
    Soustrait deux objets datetime et retourne la différence en secondes.

    Args:
        datetime1 (datetime): Le premier objet datetime.
        datetime2 (datetime): Le deuxième objet datetime.

    Returns:
        int: La différence en secondes entre datetime1 et datetime2.
    """
    year1, month1, day1, hour1, minute1, second1 = (
        datetime1.year,
        datetime1.month,
        datetime1.day,
        datetime1.hour,
        datetime1.minute,
        datetime1.second,
    )
    year2, month2, day2, hour2, minute2, second2 = (
        datetime2.year,
        datetime2.month,
        datetime2.day,
        datetime2.hour,
        datetime2.minute,
        datetime2.second,
    )
    datetime1 = datetime(year1, month1, day1, hour1, minute1, second1)
    datetime2 = datetime(year2, month2, day2, hour2, minute2, second2)

    timedelta = datetime1 - datetime2
    dt_time = int(timedelta.total_seconds())
    
    return dt_time

def generate_bearer_token():
    token = secrets.token_urlsafe(32)
    bearer_token = f"{token}"
    return bearer_token

def add_item(array, field, value):
    if array[field] is not list:
        array[field] = list(array[field], value)
    else: 
        array[field].append(value)
    return array


def dict_merge(dict1: dict, dict2: dict) -> dict:
    dict_merged = defaultdict(list)

    for key, value in dict1.items():
        dict_merged[key].append(value) if not isinstance(value, list) else dict_merged[key].extend(value)

    for key, value in dict2.items():
        dict_merged[key].append(value) if not isinstance(value, list) else dict_merged[key].extend(value)

    return dict(dict_merged)

def split_string(string, prefixes):
    sorted_prefixes = sorted(prefixes, key=len, reverse=True)
    for prefix in sorted_prefixes:
        if string.startswith(prefix):
            return prefix, string[len(prefix):]
    return None, string

def filter_deleted(data, delete_attr='deleted_at')->list:
    return [dict(item) for item in data if not hasattr(item, 'deleted_at') or  not getattr(item, delete_attr)]

def get_attribute(obj, attribute_str: str, default = None):
    """
    Retrieve an attribute from an object using a dot-separated string.

    Args:
        obj: The object from which to retrieve the attribute.
        attribute_str: A dot-separated string representing the attribute path.

    Returns:
        The value of the specified attribute.

    Example:
        user = User()
        role_name = get_attribute(user, 'role.name')
    """
    if not has_attribute(obj, attribute_str):
        return default
    
    attributes = attribute_str.split('.')
    for attr in attributes:
        obj = getattr(obj, attr)
    
    return obj

def has_attribute(obj, attribute_str: str):
    """
    Check if an object has the specified attribute.

    Args:
        obj: The object to check for the attribute.
        attribute_str: A dot-separated string representing the attribute path.

    Returns:
        True if the attribute exists, False otherwise.

    Example:
        user = User()
        if has_attribute(user, 'role.name'):
            print("User has 'role.name' attribute.")
        else:
            print("User does not have 'role.name' attribute.")
    """
    attributes = attribute_str.split('.')
    for attr in attributes:
        if not hasattr(obj, attr):
            return False
        obj = getattr(obj, attr)
    return True
def get_all_subclasses(model):
    subclasses = set()
    for subclass in model.__subclasses__():
        subclasses.add(subclass)
        subclasses.update(get_all_subclasses(subclass))
    return subclasses

def delete_keys(obj:dict, *keys):
    dict_keys = obj.keys()
    for key in keys:
        if key in dict_keys:
            del obj[key]

def try_retry(func, retry:int= 3, wait_time:int=0, default_value=None, *args, **kwargs):
    def wrapper_func(queue, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            queue.put(result)
        except Exception as e:
            queue.put(e)

    queue = Queue()
    for i in range(retry):
        t_func = Thread(target=wrapper_func, args=(queue,)+args, kwargs=kwargs)
        try:
            t_func.start()
            t_func.join()
            result = queue.queue.pop()
            if not isinstance(result, Exception):
                return result
            else:
                raise result
        except Exception as e:
            print(f"Error: {e}")
            sleep(wait_time)
    return default_value

if __name__ == '__main__':
    def test_try_retry():
        def test_func():
            print('test')
            raise Exception('test')
        return try_retry(test_func, 2, 1, 'default')
    # Example usage for testing
    pascal_case_string = "PascalCaseString"
    camel_case_string = "camel_case_string"
    file_path = "path/to/your/file.py"
    class_name = "YourClass"
    string_to_convert = "12345"
    uuid_value = "123e4567-e89b-12d3-a456-426614174001"
    datetime1 = datetime(2022, 1, 1, 12, 0, 0)
    datetime2 = datetime(2022, 1, 1, 10, 30, 0)

    print(f"Convert PascalCase to CamelCase: {to_camel_case(pascal_case_string)}")
    print(f"Convert CamelCase to PascalCase: {to_pascal_case(camel_case_string)}")
    
    # loaded_class = load_class_from_file(file_path, class_name)
    # print(f"Loaded class from file: {loaded_class}")

    integer_value = str_to_integer(string_to_convert)
    print(f"Converted string to integer: {integer_value}")

    print(f"Is valid UUID: {is_valid_uuid(uuid_value)}")

    time_difference = subtract_datetime(datetime1, datetime2)
    print(f"Time difference in seconds: {time_difference}")

    bearer_token = generate_bearer_token()
    print(f"Generated bearer token: {bearer_token}")

    dict1 = {'a': 1, 'b': [2], 'd': 'i'}
    dict2 = {'b': [6], 'c': 1, 'd': 0}
    dict_merged = dict_merge(dict1, dict2)
    print(f"Merged dictionaries: {dict_merged}")

    string_to_process = "=>example"
    prefixes = ['=', '=>', '=<', '<', '>', '!=']

    prefix_found, remainder_string = split_string(string_to_process, prefixes)
    if prefix_found:
        print("Prefix found:", prefix_found)
        print("Remainder of the string:", remainder_string)
    else:
        print("No prefix found. Unchanged string:", string_to_process)
    class User:
        def __init__(self, pseudo):
            self.pseudo = pseudo

    class Role:
        def __init__(self, nom):
            self.nom = nom

    class UserRole:
        def __init__(self, user, role):
            self.user = User(user)
            self.role = Role(role)

    user_role = UserRole('Pascal', 'admin')
    test = 'role.no'
    print(has_attribute(user_role,test)) 
    print(get_attribute(user_role,test)) 
    print(test_try_retry())
    print(try_retry(lambda : 'Hi', 2, 1, 'default'))
    


