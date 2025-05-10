# Heat Pump

The following entities are available if you have a heat pump registered against your account. The following heat pumps are known to be compatible

* Cosy 6

## Humidity Sensor

`sensor.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_{{SENSOR_CODE}}_humidity`

This represents the humidity reported by a sensor (e.g. Cosy Pod) that is associated with a heat pump.

## Temperature Sensor

`sensor.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_{{SENSOR_CODE}}_temperature`

This represents the temperature reported by a sensor (e.g. Cosy Pod) that is associated with a heat pump.

!!! warning

    There are reports that some of these sensors can report negative values in certain installations. Unfortunately, there doesn't appear to be anything in the API that determines when these sensors are or are not applicable. In these situations, you'll need to manually disable or ignore them.

## Zone

`climate.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_{{ZONE_CODE}}`

This can be used to control the target temperature and mode for a given zone (e.g. water or zone 1) linked to your heat pump. It will also display the current temperature linked to the primary sensor for the zone.

The following operation modes are available

* `Heat` - This represents as `on` in the app
* `Off` - This represents as `off` in the app
* `Auto` - This represents as `auto` in the app

In addition, there is the preset of `boost`, which activates boost mode for the zone for 1 hour. If you require boost to be on for a different amount of time, then you can use the [available service](../services.md#octopus_energyboost_heat_pump_zone).

!!! note

    If you boost and a target temperature is not defined, then a default value will be set. This will be 50 degrees C for `water` zones and 30 degrees C for all other zones.

## Lifetime Seasonal Coefficient of Performance

`sensor.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_lifetime_scop`

This represents the efficiency by the heat pump since commissioning or last reset.

## Lifetime Energy Input 

`sensor.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_lifetime_energy_input`

This represents the energy/power drawn by the heat pump since commissioning or last reset in kWh.

## Lifetime Heat Output

`sensor.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_lifetime_heat_output`

This represents the energy/heat supplied by the heat pump since commissioning or last reset in kWh.

## Live Coefficient of Performance

`sensor.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_live_cop`

This represents the instantaneous efficiency of the heat pump.

!!! note
    As this integration uses cloud polling this will inherently have a delay.

!!! info

    This sensor will report zero when the heat pump is not reporting input power, otherwise the reported COP can be inaccurate.

## Live Power Input 

`sensor.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_live_power_input`

This represents the instantaneous energy/power being drawn by the heat pump in kWh. 

!!! note
    As this integration uses cloud polling this will inherently have a delay.

## Live Heat Output

`sensor.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_live_heat_output`

This represents the instantaneous energy/heat being supplied by heat pump in kWh. 

!!! note
    As the integration uses cloud polling this will inherently have a delay.

## Live Outdoor Temp

`sensor.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_live_outdoor_temperature`

This represents the current outdoor temperature as observed by the heat pump. 

!!! note
    As the integration uses cloud polling this will inherently have a delay.

## Services

There are some services available relating to these entities that you might find useful. They can be found in the [services docs](../services.md#heat-pump).