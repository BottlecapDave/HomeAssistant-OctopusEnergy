# Services

- [Services](#services)
  - [Service octopus\_energy.purge\_invalid\_external\_statistic\_ids](#service-octopus_energypurge_invalid_external_statistic_ids)
  - [Service octopus\_energy.refresh\_previous\_consumption\_data](#service-octopus_energyrefresh_previous_consumption_data)
  - [Service octopus\_energy.update\_target\_config](#service-octopus_energyupdate_target_config)

There are a few services available within this integration, which are detailed here.

## Service octopus_energy.purge_invalid_external_statistic_ids

Service for removing all external statistics that are associated with meters that don't have an active tariff. This is useful if you've been using the integration and obtained new smart meters.

## Service octopus_energy.refresh_previous_consumption_data

Service for refreshing the consumption/cost information for a given previous consumption entity. This is useful when you've just installed the integration and want old data brought in or a previous consumption sensor fails to import (e.g. data becomes available outside of the configured offset). The service will raise a notification when the refreshing starts and finishes.

This service is only available for the following sensors

- `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption`
- `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption`

## Service octopus_energy.update_target_config

Service for updating a given [target rate's](./setup_target_rate.md) config. This allows you to change target rates sensors dynamically based on other outside criteria (e.g. you need to adjust the target hours to top up home batteries).

> Please note this is temporary and will not persist between restarts.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the target sensor whose configuration is to be updated                                                    |
| `data.target_hours`      | `yes`    | The optional number of hours the target rate sensor should come on during a 24 hour period. Must be divisible by 0.5. |
| `data.target_start_time` | `yes`    | The optional time the evaluation period should start. Must be in the format of `HH:MM`.                               |
| `data.target_end_time`   | `yes`    | The optional time the evaluation period should end. Must be in the format of `HH:MM`.                                 |
| `data.target_offset`     | `yes`    | The optional offset to apply to the target rate when it starts. Must be in the format `(+/-)HH:MM:SS`                 |

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
automations:
  - alias: Update target rate config
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
