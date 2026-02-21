# Services

There are a few services available within this integration, which are detailed here.

## Octoplus

The following services are available if your account is enrolled into [Octoplus](./entities/octoplus.md).

### octopus_energy.join_octoplus_saving_session_event

Service for joining a new saving session event. When used, it may take a couple of minutes for the other sensors to refresh the changes.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the target sensor whose configuration is to be updated. This should always point at the [saving session events](./entities/octoplus.md#saving-session-events) entity. |
| `data.event_code`      | `no`    | The code of the event to join |

#### Automation Example

For an automation example, please refer to the available [blueprint](./blueprints.md#automatically-join-saving-sessions).

### octopus_energy.redeem_octoplus_points_into_account_credit

Allows you to redeem a certain number of of Octoplus points and convert them into account credit.

!!! info
    This service is only available if you have signed up to Octoplus

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the Octoplus points that hold the points to be redeemed. This should always point at one of the [octoplus points sensor](./entities/octoplus.md#octoplus-points) entities. |
| `data.points_to_redeem`  | `no`     | The number of points to redeem. |

#### Automation Example

For automation examples, please refer to the available [blueprints](./blueprints.md#automatically-redeem-octoplus-points-for-account-credit).

## Wheel of fortune

### octopus_energy.spin_wheel_of_fortune

This service allows the user to perform a spin on the [wheel of fortune](./entities/wheel_of_fortune.md) that is awarded to users every month. No point letting them go to waste :)

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the wheel of fortune sensor that represents the type of spin to be made. This should always point at one of the [wheel of fortune sensors](./entities/wheel_of_fortune.md) entities. |

#### Automation Example

For automation examples, please refer to the available [blueprints](./blueprints.md#wheel-of-fortune).

## Cost Trackers

The following services are available if you have set up at least one [cost tracker](./setup/cost_tracker.md).

### octopus_energy.update_cost_tracker

This service allows the user to turn the tracking on/off for a given [cost tracker](./setup/cost_tracker.md) sensor.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the cost tracker sensor(s) whose configuration is to be updated. |
| `data.is_tracking_enabled`      | `no`    | Determines if tracking should be enabled (true) or disabled (false) for the specified cost trackers |

#### Automation Example

For automation examples, please refer to the available [blueprints](./blueprints.md#cost-tracker).

### octopus_energy.reset_cost_tracker

Resets a given [cost tracker](./setup/cost_tracker.md) sensor back to zero before it's normal reset time.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the cost tracker sensor(s) that should be reset. |

### octopus_energy.adjust_accumulative_cost_tracker

Allows you to adjust the cost/consumption for any given date recorded by an accumulative [cost tracker](./setup/cost_tracker.md) sensor (e.g. week or month).

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the cost tracker sensor(s) that should be updated (e.g. `sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_week` or `sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_month`). |
| `data.date`              | `no`     | The date of the data within the cost tracker to be adjusted. |
| `data.consumption`       | `no`     | The new consumption recorded against the specified date. |
| `data.cost`              | `no`     | The new cost recorded against the specified date. |

### octopus_energy.adjust_cost_tracker

Allows you to adjust the consumption for any given period recorded by a [cost tracker](./setup/cost_tracker.md) sensor representing today.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the cost tracker sensor(s) that should be updated (e.g. `sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}`). |
| `data.date`              | `no`     | The date of the data within the cost tracker to be adjusted. |
| `data.consumption`       | `no`     | The new consumption recorded against the specified date. |

## Heat Pump

The following services are available if you have a heat pump registered against your account.

### octopus_energy.boost_heat_pump_zone

Allows you to boost a given heat pump zone for a set amount of time.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the heat pump zone boost mode should be applied to (e.g. `climate.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_{{ZONE_CODE}}`). |
| `data.hours`              | `no`     | The number of hours to turn boost mode on for. This can be between 0 and 12. |
| `data.minutes`       | `no`     | The number of minutes to turn boost mode on for. This can be 0, 15, or 45. |
| `data.target_temperature`       | `yes`     | The optional target temperature to boost to. If not supplied, then the current target temperature will be used. |

!!! note

    If you boost and a target temperature is both not provided and not defined on the sensor itself, then a default value will be set. This will be 30 degrees C.

### octopus_energy.boost_water_heater

Allows you to boost a given heat pump water heater for a set amount of time.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the heat pump water heater boost mode should be applied to (e.g. `water_heater.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}`). |
| `data.hours`              | `no`     | The number of hours to turn boost mode on for. This can be between 0 and 12. |
| `data.minutes`       | `no`     | The number of minutes to turn boost mode on for. This can be 0, 15, or 45. |
| `data.target_temperature`       | `yes`     | The optional target temperature to boost to. If not supplied, then the current target temperature will be used. |

!!! note

    If you boost and a target temperature is both not provided and not defined on the sensor itself, then a default value will be set. This will be 50 degrees C.

### octopus_energy.set_heat_pump_flow_temp_config

Allows you to set the heat pump configuration for fixed and weather compensated flow temperatures, with the option to select which is active.

!!! warning
    Changing this configuration without a good understanding of heat loss and emitter output can cause cycling, defrosting, or incorrect heat delivery. 

!!! note
    Corresponding sensors will not update straight away upon calling.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | Any climate entity belonging to the heat pump which the configuration should be applied to (e.g. `climate.octopus_energy_heat_pump_{{HEAT_PUMP_ID}}_{{ZONE_CODE}}`). |
| `data.weather_comp_enabled`              | `no`     | Switches weather compensation on or off. |
| `data.weather_comp_min_temperature`       | `no`     | Minimum allowable temperature for weather compensation, typically no lower than 30. |
| `data.weather_comp_max_temperature`       | `no`     | Maximum allowable temperature for weather compensation, typically no higher than 70. |
| `data.fixed_flow_temperature`        | `no`     | If a fixed flow temperature is enabled this value will be used, typically between 30 and 70. |

## Intelligent

The following services are available if you are on an intelligent tariff.

### octopus_energy.refresh_intelligent_dispatches

Refreshes intelligent dispatches for a given account.

!!! info

    This service is only available if you have switched to [manual polling](./setup/account.md#manually-refresh-intelligent-dispatches) in your configuration.

!!! warning

    This service can only be called once every minute to a maximum of 20 times per hour.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The [dispatching](./entities/intelligent.md#is-dispatching) entity that you want to refresh the content for (e.g. `binary_sensor.octopus_energy_{{DEVICE_ID}}_intelligent_dispatching`). |

#### Automation Example

For an automation example, please refer to the available [blueprint](./blueprints.md#manual-intelligent-dispatch-refreshes).

### octopus_energy.get_point_in_time_intelligent_dispatch_history

Retrieve the intelligent dispatch history which was active for a given point in time based on up to the last 48 hours of intelligent dispatches that have been captured locally. This can be used to determine why [is dispatching](./entities/intelligent.md#is-dispatching) or [off peak](./entities/electricity.md#off-peak) might have turned on during a certain time period.

!!! info

    The OE API doesn't provide historic intelligent dispatch information, so this information is stored locally as it changes. Therefore depending on how often your dispatch information refreshes, it can take a while for data to become available.

!!! note

    The data that powers this service is available at `config/.storage/octopus_energy.intelligent_dispatches_history_{{DEVICE_ID}}`


| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The [dispatching](./entities/intelligent.md#is-dispatching) entity that you want to refresh the content for (e.g. `binary_sensor.octopus_energy_{{DEVICE_ID}}_intelligent_dispatching`). |
| `data.point_in_time`     | `no`     | The point in time to get the historic dispatch information that was active at the time.


## Miscellaneous

### octopus_energy.purge_invalid_external_statistic_ids

For removing all external statistics that are associated with meters that don't have an active tariff. This is useful if you've been using the integration and obtained new smart meters.

### octopus_energy.refresh_previous_consumption_data

For refreshing the consumption/cost information for a given previous consumption entity. This is useful when you've just installed the integration and want old data brought in or a previous consumption sensor fails to import (e.g. data becomes available outside of the configured offset). The service will raise a notification when the refreshing starts and finishes.

This service is only available for the following sensors

- `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption` (this will populate both consumption and cost)
- `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption_m3` (this will populate both consumption and cost for both m3 and kwh)

!!! information

    Due to limitations with Home Assistant entities, this service will only refresh data for the associated statistic ids used for the recommended approach in the [energy dashboard](./setup/energy_dashboard.md#previous-day-consumption). This will not update the history of the entities themselves.

!!! warning

    If you are on intelligent, the cost data will not be correct for charges outside of the normal off peak times. This is because this data isn't available.