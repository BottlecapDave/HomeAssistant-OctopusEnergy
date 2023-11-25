# Services

- [Services](#services)
  - [octopus\_energy.purge\_invalid\_external\_statistic\_ids](#octopus_energypurge_invalid_external_statistic_ids)
  - [octopus\_energy.refresh\_previous\_consumption\_data](#octopus_energyrefresh_previous_consumption_data)
  - [octopus\_energy.update\_target\_config](#octopus_energyupdate_target_config)
    - [Automation Example](#automation-example)
  - [join\_octoplus\_saving\_session\_event](#join_octoplus_saving_session_event)
    - [Automation Example](#automation-example-1)
  - [spin\_wheel\_of\_fortune](#spin_wheel_of_fortune)
    - [Automation Example](#automation-example-2)

There are a few services available within this integration, which are detailed here.

## octopus_energy.purge_invalid_external_statistic_ids

for removing all external statistics that are associated with meters that don't have an active tariff. This is useful if you've been using the integration and obtained new smart meters.

## octopus_energy.refresh_previous_consumption_data

for refreshing the consumption/cost information for a given previous consumption entity. This is useful when you've just installed the integration and want old data brought in or a previous consumption sensor fails to import (e.g. data becomes available outside of the configured offset). The service will raise a notification when the refreshing starts and finishes.

This service is only available for the following sensors

- `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption` (this will populate both consumption and cost)
- `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption` (this will populate both consumption and cost for both m3 and kwh)

## octopus_energy.update_target_config

for updating a given [target rate's](./setup_target_rate.md) config. This allows you to change target rates sensors dynamically based on other outside criteria (e.g. you need to adjust the target hours to top up home batteries).

> Please note this is temporary and will not persist between restarts.

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

## join_octoplus_saving_session_event

Service for joining a new saving session event. When used, it may take a couple of minutes for the other sensors to refresh the changes.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the target sensor whose configuration is to be updated. This should always point at the [saving session events](./entities/octoplus.md#saving-session-events) entity. |
| `data.event_code`      | `no`    | The code of the event to join |

### Automation Example

Using the [new saving session event](./events.md#new-saving-session), we can join new saving session events automatically in the following way

```yaml
- trigger:
  - platform: event
    event_type: octopus_energy_new_octoplus_saving_session
  condition: []
  action:
  - service: octopus_energy.join_octoplus_saving_session_event
    data:
      event_code: '{{ trigger.event.data["event_code"] }}'
    target:
      entity_id: event.octopus_energy_{{ACCOUNT_ID}}_octoplus_saving_session_events
  - service: persistent_notification.create
    data:
      title: "Saving Sessions Updated"
      message: >
        Joined new Octopus Energy saving session. It starts at {{ trigger.event.data["event_start"].strftime('%H:%M') }} on {{ trigger.event.data["event_start"].day }}/{{ trigger.event.data["event_start"].month }} 
```

## spin_wheel_of_fortune

This service allows the user to perform a spin on the [wheel of fortune](./entities/wheel_of_fortune.md) that is awarded to users every month. No point letting them go to waste :)

### Automation Example

We can use the following automation to automatically spin the wheel of fortune

```yaml
- mode: single
  trigger:
    - platform: numeric_state
      entity_id: sensor.octopus_energy_{{ACCOUNT_ID}}_wheel_of_fortune_spins_electricity
      above: 0
    - platform: numeric_state
      entity_id: sensor.octopus_energy_{{ACCOUNT_ID}}_wheel_of_fortune_spins_gas
      above: 0
  condition: []
  action:
    - repeat:
        count: '{{ states(trigger.entity_id) | int }}'
        sequence:
          - service: octopus_energy.spin_wheel_of_fortune
            data: {}
            target:
              entity_id: '{{ trigger.entity_id }}'
```

or you can split it up into two separate automations

```yaml
- mode: single
  trigger:
    - platform: numeric_state
      entity_id: sensor.octopus_energy_{{ACCOUNT_ID}}_wheel_of_fortune_spins_electricity
      above: 0
  condition: []
  action:
    - repeat:
        count: '{{ states('sensor.octopus_energy_{{ACCOUNT_ID}}_wheel_of_fortune_spins_electricity') | int }}'
        sequence:
          - service: octopus_energy.spin_wheel_of_fortune
            data: {}
            target:
              entity_id: sensor.octopus_energy_{{ACCOUNT_ID}}_wheel_of_fortune_spins_electricity
```

and

```yaml
- mode: single
  trigger:
    - platform: numeric_state
      entity_id: sensor.octopus_energy_{{ACCOUNT_ID}}_wheel_of_fortune_spins_gas
      above: 0
  condition: []
  action:
    - repeat:
        count: '{{ states('sensor.octopus_energy_{{ACCOUNT_ID}}_wheel_of_fortune_spins_gas') | int }}'
        sequence:
          - service: octopus_energy.spin_wheel_of_fortune
            data: {}
            target:
              entity_id: sensor.octopus_energy_{{ACCOUNT_ID}}_wheel_of_fortune_spins_gas
```