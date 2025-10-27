# Intelligent

If you are on the [intelligent tariff](https://octopus.energy/smart/intelligent-octopus/), then you'll get the following entities.

!!! warning

    If you switch to the intelligent tariff after you have installed the integration, you will need to reload the integration or restart your Home Assistant instance. You will also need to do this if you re-onboard.

## Is Dispatching

`binary_sensor.octopus_energy_{{DEVICE_ID}}_intelligent_dispatching`

This sensor is used to determine if you're within a dispatching period (i.e. "smart-charge" determined by Octopus Energy) for a **single** intelligent device. This sensor **will not** come on during a bump charge.

Depending on your [account configuration](../setup/account.md#intelligent-rates-mode), what is determined as an active dispatching period will change. If you have configured to accept [planned or started dispatches](../setup/account.md#planned-and-started-dispatches-will-turn-into-off-peak-rates), then the sensor will turn on when you're are within an active planned or started dispatch period. If you have configured to accept [only started dispatches](../setup/account.md#only-started-dispatches-will-turn-into-off-peak-rates), then the sensor will turn on when you're are within an active started dispatch period, but not planned dispatch.

!!! warning

    If you are using this to drive other automations for cheap rates (e.g. to fill batteries), you should perform additional checks to make sure your vehicle is actually charging. If it isn't, this sensor could be incorrectly on if during a dispatch outside of the standard off peak period and you will therefore not receive the off peak rate.
    
    If you are wanting to know when you are within a guaranteed off peak period, you should use the [off peak](./electricity.md#off-peak) sensor.

!!! warning

    This sensor is only partially supported for the following intelligent providers

    * OHME

    If you are supplied by one of the above providers, this sensor will never turn on. 

!!! info

    This sensor will only turn on during dispatches for a single intelligent device. If you're after a sensor that turns on during the standard off peak rates as well or cover multiple intelligent devices then you're best to use the [off peak sensor](./electricity.md#off-peak).

!!! note

    Sensor came on when you did/didn't expected it to? You can see what the state of your dispatches were at the time by using the [get_point_in_time_intelligent_dispatch_history service](../services.md#octopus_energyget_point_in_time_intelligent_dispatch_history)

| Attribute | Type | Description |
|-----------|------|-------------|
| `planned_dispatches` | `array` | An array of the dispatches that are currently planned by Octopus Energy. |
| `completed_dispatches` | `array` | An array of the dispatches that have been completed by Octopus Energy. This will only store up to the last 3 days worth of completed dispatches. This includes dispatches that were scheduled by OE and boost dispatches issued by the user. OE do not provide details on what triggered the completed dispatches. |
| `started_dispatches` | `array` | An array of the dispatches that have been planned by Octopus Energy and started. See the [FAQ](../faq.md#what-are-started-dispatches-and-how-are-they-calculated) for how this is calculated and why it exists. |
| `provider` | `string` | The provider of the intelligent features |
| `vehicle_battery_size_in_kwh` | `float` | The size of the target vehicle battery in kWh. |
| `charge_point_power_in_kw` | `float` | The power of the charge point battery in kW. |
| `current_start` | `datetime` | The date/time when the dispatching or off peak rate started |
| `current_end` | `datetime` | The date/time when the dispatching or off peak rate ends |
| `next_start` | `datetime` | The date/time when the next dispatching or off peak rate starts |
| `next_end` | `datetime` | The date/time when the next dispatching or off peak rate ends |
| `manually_refresh_dispatches` | `boolean` | Determines if manual dispatching has been enabled in the [integration config](../setup/account.md#manually-refresh-intelligent-dispatches) |

Each item in `planned_dispatch` have the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The start date/time of the dispatch |
| `end` | `datetime` | The end date/time of the dispatch |
| `source` | `string` | Determines what has caused the dispatch to be generated. Will be `SMART`, `BOOST`, `TEST` or None. |

Each item in `completed_dispatches` have the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The start date/time of the dispatch |
| `end` | `datetime` | The end date/time of the dispatch |
| `charge_in_kwh` | `float` | The amount to be charged within the dispatch period. |
| `source` | `string` | Determines what has caused the dispatch to be generated. Will be `smart-charge`, `bump-charge` or None. |
| `location` | `string` | The location of the smart charge |

Each item in `started_dispatch` have the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The start date/time of the dispatch |
| `end` | `datetime` | The end date/time of the dispatch |

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#intelligent-dispatches-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

## Current State

`sensor.octopus_energy_{{DEVICE_ID}}_intelligent_state`

This sensor displays the current state of your intelligent provider as told by the OE API for a **single** intelligent device. The value of this sensor can be one of the following

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

## Bump Charge

`switch.octopus_energy_{{DEVICE_ID}}_intelligent_bump_charge`

This sensor is used to turn on/off bump ("on-demand") charging for a **single** intelligent device.

!!! info

    This entity is not available for the following intelligent providers

    * OHME

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#intelligent-settings-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

## Smart Charge

`switch.octopus_energy_{{DEVICE_ID}}_intelligent_smart_charge`

This sensor is used to turn on/off intelligent smart charging for a **single** intelligent device.

!!! info

    This entity is not available for the following intelligent providers

    * OHME

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#intelligent-settings-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

## Charge Target

`number.octopus_energy_{{DEVICE_ID}}_intelligent_charge_target`

This sensor is used to see and set the charge target for your future intelligent charges for a **single** intelligent device.

!!! info

    This entity is not available for the following intelligent providers

    * OHME

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#intelligent-settings-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

## Target Time (Select)

`select.octopus_energy_{{DEVICE_ID}}_intelligent_target_time`

This sensor is used to see and set the target time for your future intelligent charges for a **single** intelligent device. 

This is limited to 30 minute increments between 4 and 11 to match the Octopus Energy app. This is useful if you use the app or have non-technical people interacting with the integration.

!!! info

    This entity is not available for the following intelligent providers

    * OHME

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#intelligent-settings-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

| Attribute | Type | Description |
|-----------|------|-------------|
| `raw_value` | `time` | The raw target time. This is useful if the time is set to a value outside of the range available in the select options (e.g. from another integration) |

## Target Time (Time)

`time.octopus_energy_{{DEVICE_ID}}_intelligent_target_time`

This sensor is used to see and set the target time for your future intelligent charges for a **single** intelligent device. 

This gives you finer control over the times (still within valid time periods), but may have unintended consequences with other apps (e.g. the Octopus Energy app) that use the data.

!!! info

    This entity is not available for the following intelligent providers

    * OHME

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#intelligent-settings-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). If enabled, it is advised to disable the [select based sensor](#target-time-select) as the two can get out of sync. 

## Migrating from megakid/ha_octopus_intelligent?

If you're moving to this integration from [megakid/ha_octopus_intelligent](https://github.com/megakid/ha_octopus_intelligent), below is a quick guide on what entities you should use

* `binary_sensor.octopus_intelligent_slot` - Use the [off peak sensor](./electricity.md#off-peak)
* `binary_sensor.octopus_intelligent_planned_dispatch_slot` - Use the [is dispatching sensor](#is-dispatching)
* `binary_sensor.octopus_intelligent_slot_next_1_hour`, `binary_sensor.octopus_intelligent_slot_next_2_hours` and `binary_sensor.octopus_intelligent_slot_next_3_hours` - These sensors felt like they would always fall short of peoples requirements as everyone has different time periods they wish to know about. The [off peak sensor](./electricity.md#off-peak) exposes the current and next start/end times which could be used in a template sensor to determine how long the rate is cheap for when on. Or the [target rate](../setup/target_rate.md) or [rolling target rate](../setup/rolling_target_rate.md) might help for what you need.
* `sensor.octopus_intelligent_next_offpeak_start` - The default off peak start date/time can be found as an attribute on the [off peak sensor](./electricity.md#off-peak). This can be extracted using a [template sensor](https://www.home-assistant.io/integrations/template/).
* `sensor.octopus_intelligent_offpeak_end` - The default off peak end date/time can be found as an attribute on the [off peak sensor](./electricity.md#off-peak). This can be extracted using a [template sensor](https://www.home-assistant.io/integrations/template/).
* `switch.octopus_intelligent_bump_charge` - Use the [bump charge sensor](#bump-charge)
* `switch.octopus_intelligent_smart_charging` - Use the [smart charge sensor](#smart-charge)
* `select.octopus_intelligent_target_time` - Use the [target time (time) sensor](#target-time-time) or [target time (select) sensor](#target-time-select)
* `select.octopus_intelligent_target_soc` - Use the [charge target sensor](#charge-target)