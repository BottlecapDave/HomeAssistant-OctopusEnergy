from datetime import timedelta
import logging

from homeassistant.util.dt import (utcnow, as_utc, parse_datetime)
from homeassistant.components.sensor import (
    SensorDeviceClass
)

from ...api_client import (OctopusEnergyApiClient)

from .base import (OctopusEnergyGasSensor)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyGasCurrentStandingCharge(OctopusEnergyGasSensor):
  """Sensor for displaying the current standing charge."""

  def __init__(self, client: OctopusEnergyApiClient, tariff_code, meter, point):
    """Init sensor."""
    OctopusEnergyGasSensor.__init__(self, meter, point)

    self._client = client
    self._tariff_code = tariff_code

    self._state = None
    self._latest_date = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f'octopus_energy_gas_{self._serial_number}_{self._mprn}_current_standing_charge';
    
  @property
  def name(self):
    """Name of the sensor."""
    return f'Gas {self._serial_number} {self._mprn} Current Standing Charge'

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.MONETARY

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:currency-gbp"

  @property
  def unit_of_measurement(self):
    """Unit of measurement of the sensor."""
    return "GBP"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def state(self):
    """Retrieve the latest gas standing charge"""
    return self._state

  async def async_update(self):
    """Get the current price."""
    # Find the current rate. We only need to do this every day

    utc_now = utcnow()
    if (self._latest_date == None or (self._latest_date + timedelta(days=1)) < utc_now):
      _LOGGER.debug('Updating OctopusEnergyGasCurrentStandingCharge')

      period_from = as_utc(parse_datetime(utc_now.strftime("%Y-%m-%dT00:00:00Z")))
      period_to = as_utc(parse_datetime((utc_now + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")))

      standard_charge_result = await self._client.async_get_gas_standing_charge(self._tariff_code, period_from, period_to)
      
      if standard_charge_result != None:
        self._latest_date = period_from
        self._state = standard_charge_result["value_inc_vat"] / 100

        # Adjust our period, as our gas only changes on a daily basis
        self._attributes["valid_from"] = period_from
        self._attributes["valid_to"] = period_to
      else:
        self._state = None

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = state.state
      self._attributes = {}
      for x in state.attributes.keys():
        self._attributes[x] = state.attributes[x]
    
      _LOGGER.debug(f'Restored OctopusEnergyGasCurrentStandingCharge state: {self._state}')