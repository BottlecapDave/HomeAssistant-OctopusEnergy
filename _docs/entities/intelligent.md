# Intelligent

If you are on the [intelligent tariff](https://octopus.energy/smart/intelligent-octopus/), then you'll get the following entities.

!!! warning

    If you switch to the intelligent tariff after you have installed the integration, you will need to reload the integration or restart your Home Assistant instance.

### Is Dispatching

`binary_sensor.octopus_energy_{{ACCOUNT_ID}}_intelligent_dispatching`

This sensor is used to determine if you're currently in a planned dispatch period (i.e. "smart-charge" determined by Octopus Energy) or are within the standard off peak period. This sensor **will not** come on during a bump charge.

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
| `provider` | `string` | The provider of the intelligent features |
| `vehicle_battery_size_in_kwh` | `float` | The size of the target vehicle battery in kWh. |
| `charge_point_power_in_kw` | `float` | The power of the charge point battery in kW. |
| `current_start` | `datetime` | The date/time when the dispatching or off peak rate started |
| `current_end` | `datetime` | The date/time when the dispatching or off peak rate ends |
| `next_start` | `datetime` | The date/time when the next dispatching or off peak rate starts |
| `next_end` | `datetime` | The date/time when the next dispatching or off peak rate ends |

Each item in `planned_dispatch` or `completed_dispatches` have the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The start date/time of the dispatch |
| `end` | `datetime` | The end date/time of the dispatch |
| `charge_in_kwh` | `float` | The amount to be charged within the dispatch period. |
| `source` | `string` | Determines what has caused the dispatch to be generated. Will be `smart-charge` or `bump-charge`. |
| `location` | `string` | The location of the smart charge |

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#intelligent-dispatches-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

### Current State

`sensor.octopus_energy_{{ACCOUNT_ID}}_intelligent_state`

This sensor displays the current state of your intelligent provider as told by the OE API. The value of this sensor can be one of the following

* `AUTHENTICATION_PENDING` - ready to start authentication and authorization, or auth is in progress.
* `AUTHENTICATION_FAILED` - failed to connect and ready to restart authentication and authorization.
* `AUTHENTICATION_COMPLETE`- ready to start test (if needed) or pending live where auth or telemetry is delayed.
* `TEST_CHARGE_IN_PROGRESS` - connection and smart control test has successfully started and is occurring.
* `TEST_CHARGE_FAILED` - connection or smart control test has failed or could not start, ready to retry test.
* `TEST_CHARGE_NOT_AVAILABLE` - not currently capable of smart control test (e.g. away from home or unplugged).
* `SETUP_COMPLETE` - test is complete (if needed) and device is live, but not ready for smart control.
* `SMART_CONTROL_CAPABLE` - live and ready for smart control (e.g. at home and plugged in) but none is scheduled.
* `SMART_CONTROL_IN_PROGRESS` - smart control (e.g. smart charging) is scheduled or is currently occurring.
* `BOOSTING` - user has overridden the schedule to immediately boost (e.g. bump charge now).
* `SMART_CONTROL_OFF` - smart control has been (temporarily) disabled (e.g. by the user with holiday mode).
* `SMART_CONTROL_NOT_AVAILABLE` - not currently capable of smart control (e.g. away from home or unplugged).
* `LOST_CONNECTION` - lost connection to the device, ready to re-auth (if not temporary / automatic fix).
* `RETIRED` - / de-authed (re-auth not possible, re-register device to onboard again).

### Bump Charge

`switch.octopus_energy_{{ACCOUNT_ID}}_intelligent_bump_charge`

This sensor is used to turn on/off bump ("on-demand") charging.

!!! info

    This entity is not available for the following intelligent providers

    * OHME

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#intelligent-settings-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

### Smart Charge

`switch.octopus_energy_{{ACCOUNT_ID}}_intelligent_smart_charge`

This sensor is used to turn on/off intelligent smart charging.

!!! info

    This entity is not available for the following intelligent providers

    * OHME

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#intelligent-settings-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

### Charge Target

`number.octopus_energy_{{ACCOUNT_ID}}_intelligent_charge_target`

This sensor is used to see and set the charge target for your future intelligent charges.

!!! info

    This entity is not available for the following intelligent providers

    * OHME

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#intelligent-settings-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

### Target Time

`select.octopus_energy_{{ACCOUNT_ID}}_intelligent_target_time`

This sensor is used to see and set the target time for your future intelligent charges.

!!! info

    This entity is not available for the following intelligent providers

    * OHME

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#intelligent-settings-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

!!! warning

    There is a time based sensor called `time.octopus_energy_{{ACCOUNT_ID}}_intelligent_target_time` which represents this functionality. This is a legacy sensor which will be removed in the future. 

## Migrating from megakid/ha_octopus_intelligent?

If you're moving to this integration from [megakid/ha_octopus_intelligent](https://github.com/megakid/ha_octopus_intelligent), below is a quick guide on what entities you should use

* `binary_sensor.octopus_intelligent_slot` - Use the [is dispatching sensor](#is-dispatching)
* `binary_sensor.octopus_intelligent_planned_dispatch_slot` - There is no alternative for this.
* `binary_sensor.octopus_intelligent_slot_next_1_hour`, `binary_sensor.octopus_intelligent_slot_next_2_hours` and `binary_sensor.octopus_intelligent_slot_next_3_hours` - These sensors felt like they would always fall short of peoples requirements as everyone has different time periods they wish to know about. The [is dispatching sensor](#is-dispatching) exposes the current and next start/end times which could be used in a template sensor to determine how long the rate is cheap for when on. Or the [target rate](../setup/target_rate.md) or [rolling target rate](../setup/rolling_target_rate.md) might help for what you need.
* `sensor.octopus_intelligent_next_offpeak_start` - The default off peak start date/time can be found as an attribute on the [off peak sensor](./electricity.md#off-peak). This can be extracted using a [template sensor](https://www.home-assistant.io/integrations/template/).
* `sensor.octopus_intelligent_offpeak_end` - The default off peak end date/time can be found as an attribute on the [off peak sensor](./electricity.md#off-peak). This can be extracted using a [template sensor](https://www.home-assistant.io/integrations/template/).
* `switch.octopus_intelligent_bump_charge` - Use the [bump charge sensor](#bump-charge)
* `switch.octopus_intelligent_smart_charging` - Use the [smart charge sensor](#smart-charge)
* `select.octopus_intelligent_target_time` - Use the [target time sensor](#target-time)
* `select.octopus_intelligent_target_soc` - Use the [charge target sensor](#charge-target)