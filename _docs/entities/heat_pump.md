# Heat Pump

The following entities are available if you have a heat pump registered against your account. The following heat pumps are known to be compatible

* Cosy 6

## Humidity Sensor

`sensor.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_{{SENSOR_CODE}}_humidity`

This represents the humidity reported by a sensor (e.g. Cosy Pod) that is associated with a heat pump.

## Temperature Sensor

`sensor.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_{{SENSOR_CODE}}_temperature`

This represents the temperature reported by a sensor (e.g. Cosy Pod) that is associated with a heat pump.

## Zone

`climate.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_{{ZONE_CODE}}`

This can be used to control the target temperature and mode for a given zone (e.g. water or zone 1) linked to your heat pump. It will also display the current temperature linked to the primary sensor for the zone.

The following operation modes are available

* `Heat` - This represents as `on` in the app
* `Off` - This represents as `off` in the app
* `Auto` - This represents as `auto` in the app

In addition, there is the preset of `boost`, which activates boost mode for the zone for 1 hour. If you require boost to be on for a different amount of time, then you can use the [available service](../services.md#octopus_energyboost_heat_pump_zone).