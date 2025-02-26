"""Discovery of devices with an energy definition."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.helpers import entity_registry as er
from homeassistant.config_entries import SOURCE_INTEGRATION_DISCOVERY
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import discovery_flow
from homeassistant.const import (
    UnitOfEnergy
)

from .const import (
    CONFIG_COST_TRACKER_DISCOVERY_ACCOUNT_ID,
    CONFIG_COST_TRACKER_DISCOVERY_NAME,
    CONFIG_COST_TRACKER_TARGET_ENTITY_ID,
    CONFIG_KIND,
    CONFIG_KIND_COST_TRACKER,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

class DiscoveryManager:
    """Device Discovery."""

    def __init__(self, hass: HomeAssistant, account_id: str) -> None:
        """Init."""
        self._hass = hass
        self._account_id = account_id

    async def start_discovery(self) -> None:
        """Start the discovery procedure."""
        _LOGGER.debug("Start auto discovering of entities")
        entity_registry = er.async_get(self._hass)
        entities = entity_registry.entities.items()
        config_entries = self._hass.config_entries.async_entries(DOMAIN, include_ignore=False)
        for item in entities:
            unique_id: str = item[1].unique_id

            if "octopus_energy" in unique_id:
                continue

            if item[1].disabled_by is not None:
                continue

            if item[1].unit_of_measurement != UnitOfEnergy.KILO_WATT_HOUR:
                continue

            config_exists = False
            for entry in config_entries:
                config_entry_data = dict(entry.data)

                if entry.options:
                    config_entry_data.update(entry.options)

                if config_entry_data[CONFIG_KIND] == CONFIG_KIND_COST_TRACKER and config_entry_data[CONFIG_COST_TRACKER_TARGET_ENTITY_ID] == item[1].entity_id:
                    config_exists = True
                    break

            if config_exists:
                continue

            self._init_entity_discovery(item[1])
            

        _LOGGER.debug("Done auto discovering devices")

    @callback
    def _init_entity_discovery(
        self,
        entity_entry
    ) -> None:
        """Dispatch the discovery flow for a given entity."""
        discovery_data: dict[str, Any] = {
            CONFIG_KIND: CONFIG_KIND_COST_TRACKER,
            CONFIG_COST_TRACKER_TARGET_ENTITY_ID: entity_entry.entity_id,
            CONFIG_COST_TRACKER_DISCOVERY_ACCOUNT_ID: self._account_id,
            CONFIG_COST_TRACKER_DISCOVERY_NAME:  f"{entity_entry.original_name if entity_entry.name is None else entity_entry.name} Cost Tracker ({self._account_id})"
        }

        discovery_key = discovery_flow.DiscoveryKey(
            domain=DOMAIN,
            key=f"ct_{entity_entry.entity_id}",
            version=1,
        )

        discovery_flow.async_create_flow(
            self._hass,
            DOMAIN,
            context={
                "source": SOURCE_INTEGRATION_DISCOVERY
            },
            data=discovery_data,
            discovery_key=discovery_key
        )