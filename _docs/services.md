# Services

There are a few services available within this integration, which are detailed here.

## octopus_energy.purge_invalid_external_statistic_ids

For removing all external statistics that are associated with meters that don't have an active tariff. This is useful if you've been using the integration and obtained new smart meters.

## octopus_energy.refresh_previous_consumption_data

For refreshing the consumption/cost information for a given previous consumption entity. This is useful when you've just installed the integration and want old data brought in or a previous consumption sensor fails to import (e.g. data becomes available outside of the configured offset). The service will raise a notification when the refreshing starts and finishes.

This service is only available for the following sensors

- `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption` (this will populate both consumption and cost)
- `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption` (this will populate both consumption and cost for both m3 and kwh)

## octopus_energy.update_target_config

For updating a given [target rate's](./setup/target_rate.md) config. This allows you to change target rates sensors dynamically based on other outside criteria (e.g. you need to adjust the target hours to top up home batteries).

!!! info

    This is temporary and will not persist between restarts.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the target sensor whose configuration is to be updated.                                                   |
| `data.target_hours`      | `yes`    | The optional number of hours the target rate sensor should come on during a 24 hour period. Must be divisible by 0.5. |
| `data.target_start_time` | `yes`    | The optional time the evaluation period should start. Must be in the format of `HH:MM`.                               |
| `data.target_end_time`   | `yes`    | The optional time the evaluation period should end. Must be in the format of `HH:MM`.                                 |
| `data.target_offset`     | `yes`    | The optional offset to apply to the target rate when it starts. Must be in the format `(+/-)HH:MM:SS`.                |

### Automation Example

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
trigger:
  - platform: state
    entity_id:
      - input_number.octopus_energy_target_hours
      - input_text.octopus_energy_target_from
      - input_text.octopus_energy_target_to
      - input_text.octopus_energy_target_offset
condition: []
action:
  - service: octopus_energy.update_target_config
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

## octopus_energy.join_octoplus_saving_session_event

Service for joining a new saving session event. When used, it may take a couple of minutes for the other sensors to refresh the changes.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the target sensor whose configuration is to be updated. This should always point at the [saving session events](./entities/octoplus.md#saving-session-events) entity. |
| `data.event_code`      | `no`    | The code of the event to join |

### Automation Example

For an automation example, please refer to the available [blueprint](./blueprints.md#automatically-join-saving-sessions).

## octopus_energy.spin_wheel_of_fortune

This service allows the user to perform a spin on the [wheel of fortune](./entities/wheel_of_fortune.md) that is awarded to users every month. No point letting them go to waste :)

!!! warning

    Due to an ongoing issue with the underlying API, this will not award octopoints if used. If you are on Octoplus, it is advised not to use this service.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the wheel of fortune sensor that represents the type of spin to be made. This should always point at one of the [wheel of fortune sensors](./entities/wheel_of_fortune.md) entities. |

### Automation Example

For automation examples, please refer to the available [blueprints](./blueprints.md#wheel-of-fortune).

## octopus_energy.redeem_octoplus_points_into_account_credit

Allows you to redeem a certain number of of Octoplus points and convert them into account credit.

!!! info
    This service is only available if you have signed up to Octoplus

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the Octoplus points that hold the points to be redeemed. This should always point at one of the [octoplus points sensor](./entities/octoplus.md#octoplus-points) entities. |
| `data.points_to_redeem`  | `no`     | The number of points to redeem. |

## octopus_energy.update_cost_tracker

This service allows the user to turn the tracking on/off for a given [cost tracker](./setup/cost_tracker.md) sensor.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the cost tracker sensor(s) whose configuration is to be updated. |
| `data.is_tracking_enabled`      | `no`    | Determines if tracking should be enabled (true) or disabled (false) for the specified cost trackers |

### Automation Example

For automation examples, please refer to the available [blueprints](./blueprints.md#cost-tracker).

## octopus_energy.reset_cost_tracker

Resets a given [cost tracker](./setup/cost_tracker.md) sensor back to zero before it's normal reset time.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the cost tracker sensor(s) that should be reset. |

## octopus_energy.adjust_accumulative_cost_tracker

Allows you to adjust the cost/consumption for any given date recorded by an accumulative [cost tracker](./setup/cost_tracker.md) sensor (e.g. week or month).

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the cost tracker sensor(s) that should be updated (e.g. `sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_week` or `sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_month`). |
| `data.date`              | `no`     | The date of the data within the cost tracker to be adjusted. |
| `data.consumption`       | `no`     | The new consumption recorded against the specified date. |
| `data.cost`              | `no`     | The new cost recorded against the specified date. |

## octopus_energy.adjust_cost_tracker

Allows you to adjust the consumption for any given period recorded by a [cost tracker](./setup/cost_tracker.md) sensor representing today.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the cost tracker sensor(s) that should be updated (e.g. `sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}`). |
| `data.date`              | `no`     | The date of the data within the cost tracker to be adjusted. |
| `data.consumption`       | `no`     | The new consumption recorded against the specified date. |