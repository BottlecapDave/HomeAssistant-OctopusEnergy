from datetime import datetime

from homeassistant.helpers import issue_registry as ir

from ..const import CONFIG_TARGET_NAME, DOMAIN
from ..config.target_rates import validate_target_rate_config

def check_for_errors(hass, config, account_info, now: datetime):
  if account_info is not None:
    errors = validate_target_rate_config(config, account_info, now)
    keys = list(errors.keys())
    target_rate_name = config[CONFIG_TARGET_NAME]
    repair_key = f"invalid_target_rate_{target_rate_name}"
    if len(keys) > 0:
      ir.async_create_issue(
        hass,
        DOMAIN,
        repair_key,
        is_fixable=False,
        severity=ir.IssueSeverity.ERROR,
        learn_more_url="https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/repairs/invalid_target_rate",
        translation_key="invalid_target_rate",
        translation_placeholders={ "name": target_rate_name },
      )
    else:
      ir.async_delete_issue(hass, DOMAIN, repair_key)