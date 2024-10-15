from decimal import Decimal
import pytest

from custom_components.octopus_energy.target_rates import create_weighting

@pytest.mark.asyncio
@pytest.mark.parametrize("config,number_of_slots,expected_weighting",[
  (None, 3, None),
  ("", 3, None),
  (" ", 3, None),
  ("", 0, None),
  # Integers
  ("1", 3, [Decimal('1')]),
  ("1,2,3", 3, [Decimal('1'), Decimal('2'), Decimal('3')]),
  ("2,*,3", 4, [Decimal('2'), Decimal('1'), Decimal('1'), Decimal('3')]),
  ("2,4,*,3", 5, [Decimal('2'), Decimal('4'), Decimal('1'), Decimal('1'), Decimal('3')]),
  ("2,*,3,4", 5, [Decimal('2'), Decimal('1'), Decimal('1'), Decimal('3'), Decimal('4')]),
  ("*,2,3", 4, [Decimal('1'), Decimal('1'), Decimal('2'), Decimal('3')]),
  ("*,2", 4, [Decimal('1'), Decimal('1'), Decimal('1'), Decimal('2')]),
  ("2,3,*", 4, [Decimal('2'), Decimal('3'), Decimal('1'), Decimal('1')]),
  ("2,*", 4, [Decimal('2'), Decimal('1'), Decimal('1'), Decimal('1')]),

  ("10", 3, [Decimal('10')]),
  ("10,20,30", 3, [Decimal('10'), Decimal('20'), Decimal('30')]),
  ("20,*,30", 4, [Decimal('20'), Decimal('1'), Decimal('1'), Decimal('30')]),
  ("20,40,*,30", 5, [Decimal('20'), Decimal('40'), Decimal('1'), Decimal('1'), Decimal('30')]),
  ("20,*,30,40", 5, [Decimal('20'), Decimal('1'), Decimal('1'), Decimal('30'), Decimal('40')]),
  ("*,20,30", 4, [Decimal('1'), Decimal('1'), Decimal('20'), Decimal('30')]),
  ("*,20", 4, [Decimal('1'), Decimal('1'), Decimal('1'), Decimal('20')]),
  ("20,30,*", 4, [Decimal('20'), Decimal('30'), Decimal('1'), Decimal('1')]),
  ("20,*", 4, [Decimal('20'), Decimal('1'), Decimal('1'), Decimal('1')]),

  # Decimals
  ("1.1", 3, [Decimal('1.1')]),
  ("1.1,2.2,3.3", 3, [Decimal('1.1'), Decimal('2.2'), Decimal('3.3')]),
  ("2.2,*,3.3", 4, [Decimal('2.2'), Decimal('1'), Decimal('1'), Decimal('3.3')]),
  ("2.2,4.4,*,3.3", 5, [Decimal('2.2'), Decimal('4.4'), Decimal('1'), Decimal('1'), Decimal('3.3')]),
  ("2.2,*,3.3,4.4", 5, [Decimal('2.2'), Decimal('1'), Decimal('1'), Decimal('3.3'), Decimal('4.4')]),
  ("*,2.2,3.3", 4, [Decimal('1'), Decimal('1'), Decimal('2.2'), Decimal('3.3')]),
  ("*,2.2", 4, [Decimal('1'), Decimal('1'), Decimal('1'), Decimal('2.2')]),
  ("2.2,3.3,*", 4, [Decimal('2.2'), Decimal('3.3'), Decimal('1'), Decimal('1')]),
  ("2.2,*", 4, [Decimal('2.2'), Decimal('1'), Decimal('1'), Decimal('1')]),

  ("10.1", 3, [Decimal('10.1')]),
  ("10.1,20.2,30.3", 3, [Decimal('10.1'), Decimal('20.2'), Decimal('30.3')]),
  ("20.2,*,30.3", 4, [Decimal('20.2'), Decimal('1'), Decimal('1'), Decimal('30.3')]),
  ("20.2,40.4,*,30.3", 5, [Decimal('20.2'), Decimal('40.4'), Decimal('1'), Decimal('1'), Decimal('30.3')]),
  ("20.2,*,30.3,40.4", 5, [Decimal('20.2'), Decimal('1'), Decimal('1'), Decimal('30.3'), Decimal('40.4')]),
  ("*,20.2,30.3", 4, [Decimal('1'), Decimal('1'), Decimal('20.2'), Decimal('30.3')]),
  ("*,20.2", 4, [Decimal('1'), Decimal('1'), Decimal('1'), Decimal('20.2')]),
  ("20.2,30.3,*", 4, [Decimal('20.2'), Decimal('30.3'), Decimal('1'), Decimal('1')]),
  ("20.2,*", 4, [Decimal('20.2'), Decimal('1'), Decimal('1'), Decimal('1')]),
])
async def test_when_create_weighting_called_then_valid_weighting_returned(config, number_of_slots, expected_weighting):
  actual_weighting = create_weighting(config, number_of_slots)

  if expected_weighting is None:
    assert actual_weighting == expected_weighting
  else:
    assert len(actual_weighting) == len(expected_weighting)
    for i in range(len(actual_weighting)):
      assert actual_weighting[i] == expected_weighting[i]

@pytest.mark.asyncio
@pytest.mark.parametrize("config",[
  ("*,1,*"),
  ("a,*"),
])
async def test_when_create_weighting_called_with_invalid_config_then_error_raised(config: str):
  exception_raised = False
  try:
    create_weighting(config, 3)
  except:
    exception_raised = True

  assert exception_raised == True
