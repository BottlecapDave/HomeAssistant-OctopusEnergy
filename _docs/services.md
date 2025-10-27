# Services

There are a few services available within this integration, which are detailed here.

## Target Rates

The following services are available if you have set up at least one [target rate](./setup/target_rate.md).

### octopus_energy.update_target_config

For updating a given [target rate's](./setup/target_rate.md) config. This allows you to change target rates sensors dynamically based on other outside criteria (e.g. you need to adjust the target hours to top up home batteries).

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the target sensor whose configuration is to be updated.                                                   |
| `data.target_hours`      | `yes`    | The optional number of hours the target rate sensor should come on during a 24 hour period. Must be divisible by 0.5. |
| `data.target_start_time` | `yes`    | The optional time the evaluation period should start. Must be in the format of `HH:MM`.                               |
| `data.target_end_time`   | `yes`    | The optional time the evaluation period should end. Must be in the format of `HH:MM`.                                 |
| `data.target_offset`     | `yes`    | The optional offset to apply to the target rate when it starts. Must be in the format `(+/-)HH:MM:SS`.                |
| `data.target_minimum_rate`     | `yes`    | The optional minimum rate the selected rates should not go below. |
| `data.target_maximum_rate`     | `yes`    | The optional maximum rate the selected rates should not go above. |
| `data.target_weighting`     | `yes`    | The optional weighting that should be applied to the selected rates. |
| `data.persist_changes` | `yes` | Determines if the changes should be persisted to the original configuration or should be temporary and reset upon integration reload. If not supplied, then the changes are temporary |

#### Automation Example

This can be used via automations in the following way. Assuming we have the following inputs.

```yaml
input_number:
  octopus_energy_target_hours:
    name: Octopus Energy Target Hours
    min: 0
    max: 24

input_text:
  # From/to would ideally use input_datetime, but we need the time in a different format
  octopus_energy_target_from:
    name: Octopus Energy Target From
    initial: "00:00"
  octopus_energy_target_to:
    name: Octopus Energy Target To
    initial: "00:00"
  octopus_energy_target_offset:
    name: Octopus Energy Target Offset
    initial: "-00:00:00"
```

Then an automation might look like the following

```yaml
mode: single
alias: Update target rate config
triggers:
  - trigger: state
    entity_id:
      - input_number.octopus_energy_target_hours
      - input_text.octopus_energy_target_from
      - input_text.octopus_energy_target_to
      - input_text.octopus_energy_target_offset
conditions: []
actions:
  - action: octopus_energy.update_target_config
    data:
      target_hours: >
        "{{ states('input_number.octopus_energy_target_hours') | string }}"
      target_start_time: >
        {{ states('input_text.octopus_energy_target_from') }}
      target_end_time: >
        {{ states('input_text.octopus_energy_target_to') }}
      target_offset: >
        {{ states('input_text.octopus_energy_target_offset') }}
    target:
      entity_id: binary_sensor.octopus_energy_target_example
```

## Rolling Target Rates

The following services are available if you have set up at least one [rolling target rate](./setup/rolling_target_rate.md).

### octopus_energy.update_rolling_target_config

For updating a given [rolling target rate's](./setup/rolling_target_rate.md) config. This allows you to change rolling target rates sensors dynamically based on other outside criteria (e.g. you need to adjust the target hours to top up home batteries).

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the target sensor whose configuration is to be updated.                                                   |
| `data.target_hours`      | `yes`    | The optional number of hours the target rate sensor should come on during a 24 hour period. Must be divisible by 0.5. |
| `data.target_look_ahead_hours` | `yes`    | The optional number of hours worth of rates the sensor should look at for the evaluation period.                               |
| `data.target_offset`     | `yes`    | The optional offset to apply to the target rate when it starts. Must be in the format `(+/-)HH:MM:SS`.                |
| `data.target_minimum_rate`     | `yes`    | The optional minimum rate the selected rates should not go below. |
| `data.target_maximum_rate`     | `yes`    | The optional maximum rate the selected rates should not go above. |
| `data.target_weighting`     | `yes`    | The optional weighting that should be applied to the selected rates. |
| `data.persist_changes` | `yes` | Determines if the changes should be persisted to the original configuration or should be temporary and reset upon integration reload. If not supplied, then the changes are temporary |

#### Automation Example

This can be used via automations in the following way. Assuming we have the following inputs.

```yaml
input_number:
  octopus_energy_rolling_target_hours:
    name: Octopus Energy Rolling Target Hours
    min: 0
    max: 24
  octopus_energy_rolling_target_look_ahead_hours:
    name: Octopus Energy Rolling Target Look Ahead Hours
    min: 0
    max: 24

input_text:
  octopus_energy_target_offset:
    name: Octopus Energy Target Offset
    initial: "-00:00:00"
```

Then an automation might look like the following

```yaml
mode: single
alias: Update target rate config
triggers:
  - trigger: state
    entity_id:
      - input_number.octopus_energy_rolling_target_hours
      - input_number.octopus_energy_rolling_target_look_ahead_hours
      - input_text.octopus_energy_target_offset
conditions: []
actions:
  - action: octopus_energy.update_target_config
    data:
      target_hours: >
        "{{ states('input_number.octopus_energy_target_hours') | string }}"
      target_look_ahead_hours: >
        "{{ states('input_number.octopus_energy_rolling_target_look_ahead_hours') | string }}"
      target_offset: >
        {{ states('input_text.octopus_energy_target_offset') }}
    target:
      entity_id: binary_sensor.octopus_energy_rolling_target_example
```

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

### octopus_energy.register_rate_weightings

Allows you to configure weightings against rates at given times using factors external to the integration. These are applied when calculating [target rates](./setup/target_rate.md#external-rate-weightings) or [rolling target rates](./setup/rolling_target_rate.md#external-rate-weightings).

Rate weightings are added to any existing rate weightings that have been previously configured. Any rate weightings that are more than 24 hours old are removed. Any rate weightings for periods that have been previously configured are overridden. 

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the electricity current rate sensor for the rates the weighting should be applied to (e.g. `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_rate`). |
| `data.weightings`        | `no`     | The collection of weightings to add. Each item in the array should represent a given 30 minute period. Example array is `[{ "start": "2025-01-01T00:00:00Z", "end": "2025-01-01T00:30:00Z", "weighting": 0.1 }]` |

#### Automation Example

This automation adds weightings based on the national grids carbon intensity, as provided by [Carbon Intensity](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity).

```yaml
- alias: Carbon Intensity Rate Weightings
  triggers:
  - trigger: state
    entity_id: event.carbon_intensity_national_current_day_rates
  actions:
  - action: octopus_energy.register_rate_weightings
    target:
      entity_id: sensor.octopus_energy_electricity_xxx_xxx_current_rate
    data:
      weightings: >
        {% set forecast = state_attr('event.carbon_intensity_national_current_day_rates', 'rates') + state_attr('event.carbon_intensity_national_next_day_rates', 'rates') %}
        {% set ns = namespace(list = [])  %}   {%- for a in forecast -%} 
          {%- set ns.list = ns.list + [{ "start": a.from.strftime('%Y-%m-%dT%H:%M:%SZ'), "end": a.to.strftime('%Y-%m-%dT%H:%M:%SZ'), "weighting": a.intensity_forecast | float }] -%} 
        {%- endfor -%} {{ ns.list }}
```
