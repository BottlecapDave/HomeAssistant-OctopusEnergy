import pytest

from custom_components.octopus_energy.target_rates import create_weighting

@pytest.mark.asyncio
@pytest.mark.parametrize("config,number_of_slots,expected_weighting",[
  (None, 3, None),
  ("", 3, None),
  (" ", 3, None),
  ("", 0, None),
  ("1", 3, [1]),
  ("1,2,3", 3, [1,2,3]),
  ("2,*,3", 4, [2,1,1,3]),
  ("2,4,*,3", 5, [2,4,1,1,3]),
  ("2,*,3,4", 5, [2,1,1,3,4]),
  ("*,2,3", 4, [1,1,2,3]),
  ("*,2", 4, [1,1,1,2]),
  ("2,3,*", 4, [2,3,1,1]),
  ("2,*", 4, [2,1,1,1]),
])
async def test_when_create_weighting_called_then_valid_weighting_returned(config, number_of_slots, expected_weighting):
  actual_weighting = create_weighting(config, number_of_slots)
  assert actual_weighting == expected_weighting

@pytest.mark.asyncio
async def test_when_create_weighting_called_with_invalid_config_then_error_raised():
  exception_raised = False
  try:
    create_weighting("*,1,*", 3)
  except:
    exception_raised = True

  assert exception_raised == True
