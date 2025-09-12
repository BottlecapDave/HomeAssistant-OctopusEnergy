import pytest

from custom_components.octopus_energy.utils.repairs import safe_repair_key

@pytest.mark.asyncio
async def test_safe_repair_key_when_ids_provided_then_ids_hashed():
  # Act
  result = safe_repair_key("my_repair_notice_{}_{}", "id1", "id2")
  result2 = safe_repair_key("my_repair_notice_{}_{}", "id1", "id2")

  assert result == "my_repair_notice_f3436f50b2f7f1613ad142dbce1d24801d9daaabc45ecb2db909251a214c9840_b459afddb3a09621ee29b78b3968e566d7fb0001d96395d54030eb703b0337a9"
  assert result == result2

@pytest.mark.asyncio
async def test_safe_repair_key_when_no_ids_provided_then_value_returned_unchanged():
  # Act
  result = safe_repair_key("my_repair_notice")

  assert result == "my_repair_notice"

@pytest.mark.asyncio
async def test_safe_repair_key_when_non_format_string_provided_then_value_returned_unchanged():
  # Act
  result = safe_repair_key("my_repair_notice", "id1", "id2")

  assert result == "my_repair_notice"