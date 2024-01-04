# Intelligent

If you are on the [intelligent tariff](https://octopus.energy/smart/intelligent-octopus/), then you'll get the following entities.

!!! warning

    If you switch to the intelligent tariff after you have installed the integration, you will need to reload the integration or restart your Home Assistant instance.

### Is Dispatching

`binary_sensor.octopus_energy_{{ACCOUNT_ID}}_intelligent_dispatching`

This sensor is used to determine if you're currently in a planned dispatch period (i.e. "smart-charge" determined by Octopus Energy) or are within the standard off peak period.

!!! warning

    If you are using this to drive other automations for cheap rates (e.g. to fill batteries), you should perform additional checks to make sure your vehicle is actually charging. If it isn't, this sensor could be incorrectly on if during a dispatch outside of the standard off peak period and you will therefore not receive the off peak rate.
    
    If you are wanting to know when you are within a guaranteed off peak period, you should use the [off peak](./electricity.md#off-peak) sensor.

!!! info

    This sensor is only partially supported for the following intelligent providers

    * OHME

    If you are supplied by one of the above providers, `planned_dispatches` will always return an empty collection and this entity will only turn on when within the standard off peak period.

| Attribute | Type | Description |
|-----------|------|-------------|
| `planned_dispatches` | `array` | An array of the dispatches that are currently planned by Octopus Energy. |
| `completed_dispatches` | `array` | An array of the dispatches that have been completed by Octopus Energy. This will only store up to the last 3 days worth of completed dispatches. |
| `last_evaluated` | `datetime` | The date/time the dispatching information was last evaluated. |
| `provider` | `string` | The provider of the intelligent features |
| `vehicle_battery_size_in_kwh` | `float` | The size of the target vehicle battery in kWh. |
| `charge_point_power_in_kw` | `float` | The power of the charge point battery in kW. |
| `last_evaluated` | `datetime` | The date/time the value was last evaluated |
| `data_last_retrieved` | `datetime` | The date/time the underlying data was last retrieved from Octopus Energy APIs |

### Bump Charge

`switch.octopus_energy_{{ACCOUNT_ID}}_intelligent_bump_charge`

This sensor is used to turn on/off bump ("on-demand") charging.

!!! info

    This entity is not available for the following intelligent providers

    * OHME

| Attribute | Type | Description |
|-----------|------|-------------|
| `last_evaluated` | `datetime` | The date/time the value was last evaluated |
| `data_last_retrieved` | `datetime` | The date/time the underlying data was last retrieved from Octopus Energy APIs |

### Smart Charge

`switch.octopus_energy_{{ACCOUNT_ID}}_intelligent_smart_charge`

This sensor is used to turn on/off intelligent smart charging.

!!! info

    This entity is not available for the following intelligent providers

    * OHME

| Attribute | Type | Description |
|-----------|------|-------------|
| `last_evaluated` | `datetime` | The date/time the value was last evaluated |
| `data_last_retrieved` | `datetime` | The date/time the underlying data was last retrieved from Octopus Energy APIs |

### Charge Limit

`number.octopus_energy_{{ACCOUNT_ID}}_intelligent_charge_limit`

This sensor is used to see and set the charge limit for your future intelligent charges.

!!! info

    This entity is not available for the following intelligent providers

    * OHME

| Attribute | Type | Description |
|-----------|------|-------------|
| `last_evaluated` | `datetime` | The date/time the value was last evaluated |
| `data_last_retrieved` | `datetime` | The date/time the underlying data was last retrieved from Octopus Energy APIs |

### Ready Time

`time.octopus_energy_{{ACCOUNT_ID}}_intelligent_ready_time`

This sensor is used to see and set the ready time for your future intelligent charges.

!!! info

    This entity is not available for the following intelligent providers

    * OHME

| Attribute | Type | Description |
|-----------|------|-------------|
| `last_evaluated` | `datetime` | The date/time the value was last evaluated |
| `data_last_retrieved` | `datetime` | The date/time the underlying data was last retrieved from Octopus Energy APIs |
