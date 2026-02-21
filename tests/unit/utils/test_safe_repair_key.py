import pytest

from custom_components.octopus_energy.utils.repairs import safe_repair_key

@pytest.mark.asyncio
async def test_safe_repair_key_when_ids_provided_then_ids_hashed():
  # Act
  ids = ("id1", "id2", True, 1, None)
  result = safe_repair_key("my_repair_notice_{}_{}_{}_{}_{}", *ids)
  result2 = safe_repair_key("my_repair_notice_{}_{}_{}_{}_{}", *ids)

  parts = result.split("_")
  assert len(parts) == len(ids) + 3
  assert result == "my_repair_notice_f3436f50b2f7f1613ad142dbce1d24801d9daaabc45ecb2db909251a214c9840_b459afddb3a09621ee29b78b3968e566d7fb0001d96395d54030eb703b0337a9_3cbc87c7681f34db4617feaa2c8801931bc5e42d8d0f560e756dd4cd92885f18_6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b_dc937b59892604f5a86ac96936cd7ff09e25f18ae6b758e8014a24c7fa039e91"
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