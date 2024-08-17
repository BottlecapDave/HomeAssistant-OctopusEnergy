def assert_errors_not_present(errors, config_keys: list, key_to_ignore: str = None):
  for key in config_keys:
    if key_to_ignore is not None and key == key_to_ignore:
      continue
      
    assert key not in errors