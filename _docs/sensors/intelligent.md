# Intelligent Sensors

If you are on the [intelligent tariff](https://octopus.energy/smart/intelligent-octopus/), then you'll get the following sensors.

> Please note: If you switch to the intelligent tariff after you have installed the integration, you will need to reload the integration or restart your Home Assistant instance.

- [Intelligent Sensors](#intelligent-sensors)
    - [Is Dispatching](#is-dispatching)
    - [Bump Charge](#bump-charge)
    - [Smart Charge](#smart-charge)
    - [Charge Limit](#charge-limit)
    - [Ready Time](#ready-time)

### Is Dispatching

`binary_sensor.octopus_energy_intelligent_dispatching`

This sensor is used to determine if you're currently in a planned dispatch period (i.e. "smart-charge" determined by Octopus Energy) or are within the off peak period.

| Attribute | Type | Description |
|-----------|------|-------------|
| `planned_dispatches` | `array` | An array of the dispatches that are currently planned by Octopus Energy |
| `completed_dispatches` | `array` | An array of the dispatches that have been completed by Octopus Energy. This will only store up to the last 3 days worth of completed dispatches. |
| `last_updated_timestamp` | `datetime` | The date/time the dispatching information was last retrieved from Octopus Energy. |
| `vehicle_battery_size_in_kwh` | `float` | The size of the target vehicle battery in kwh |
| `charge_point_power_in_kw` | `float` | The power of the charge point battery in kw |

### Bump Charge

`switch.octopus_energy_intelligent_bump_charge`

This sensor is used to turn on/off bump charging

### Smart Charge

`switch.octopus_energy_intelligent_smart_charge`

This sensor is used to turn on/off intelligent smart charging

### Charge Limit

`number.octopus_energy_intelligent_charge_limit`

This sensor is used to see and set the charge limit for your future intelligent charges.

| Attribute | Type | Description |
|-----------|------|-------------|
| `last_updated_timestamp` | `datetime` | The date/time the information was last retrieved from Octopus Energy. |

### Ready Time

`time.octopus_energy_intelligent_ready_time`

This sensor is used to see and set the ready time for your future intelligent charges.

| Attribute | Type | Description |
|-----------|------|-------------|
| `last_updated_timestamp` | `datetime` | The date/time the information was last retrieved from Octopus Energy. |