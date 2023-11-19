import re
from datetime import datetime

attribute_keys_to_skip = ['mpan', 'mprn']

def dict_to_typed_dict(data: dict):
  if data is not None:
    new_data = data.copy()
    keys = new_data.keys()
    for key in keys:
      if isinstance(new_data[key], str) and key not in attribute_keys_to_skip:
        # Check for integers
        matches = re.search("^[0-9]+$", new_data[key])
        if (matches is not None):
          new_data[key] = int(new_data[key])
          continue
        
        # Check for floats/decimals
        matches = re.search("^[0-9]+\\.[0-9]+$", new_data[key])
        if (matches is not None):
          new_data[key] = float(new_data[key])
          continue

        # Check for dates
        is_date = True
        try:
          data_as_datetime = datetime.fromisoformat(new_data[key].replace('Z', '+00:00'))
          new_data[key] = data_as_datetime
          continue
        except:
          # Do nothing
          is_date = False

      elif isinstance(new_data[key], dict):
        print("test")
        new_data[key] = dict_to_typed_dict(new_data[key])
      elif isinstance(new_data[key], list):
        new_array = []
        for item in new_data[key]:
          new_array.append(dict_to_typed_dict(item))

        new_data[key] = new_array

    return new_data
  
  return None