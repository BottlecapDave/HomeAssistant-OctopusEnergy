# Events

The following events are raised by the integration. These events power various entities and can also be used within automations.

## Electricity Current Day Rates

`octopus_energy_electricity_current_day_rates`

This is fired when the current day rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the current day |
| `tariff_code` | `string` | The tariff code associated with current day's rates |
| `mpan` | `string` | The mpan of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |
| `min_rate` | `float` | The minimum/lowest rate in the discovered rates collection |
| `max_rate` | `float` | The maximum/highest rate in the discovered rates collection |
| `average_rate` | `float` | The average rate in the discovered rates collection |

### Automation Example

```yaml
- trigger:
  - platform: event
    event_type: octopus_energy_electricity_current_day_rates
  condition: []
  action:
  - service: persistent_notification.create
    data:
      title: "Rates Updated"
      message: >
        New rates available for {{ trigger.event.data.mpan }}. Starting value is {{ trigger.event.data.rates[0]["value_inc_vat"] }}
```

## Electricity Previous Day Rates

`octopus_energy_electricity_previous_day_rates`

This is fired when the previous day rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the previous day |
| `tariff_code` | `string` | The tariff code associated with previous day's rates |
| `mpan` | `string` | The mpan of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |
| `min_rate` | `float` | The minimum/lowest rate in the discovered rates collection |
| `max_rate` | `float` | The maximum/highest rate in the discovered rates collection |
| `average_rate` | `float` | The average rate in the discovered rates collection |

### Automation Example

```yaml
- trigger:
  - platform: event
    event_type: octopus_energy_electricity_previous_day_rates
  condition: []
  action:
  - service: persistent_notification.create
    data:
      title: "Rates Updated"
      message: >
        New rates available for {{ trigger.event.data.mpan }}. Starting value is {{ trigger.event.data.rates[0]["value_inc_vat"] }}
```

## Electricity Next Day Rates

`octopus_energy_electricity_next_day_rates`

This is fired when the next day rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the next day |
| `tariff_code` | `string` | The tariff code associated with next day's rates |
| `mpan` | `string` | The mpan of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |
| `min_rate` | `float` | The minimum/lowest rate in the discovered rates collection |
| `max_rate` | `float` | The maximum/highest rate in the discovered rates collection |
| `average_rate` | `float` | The average rate in the discovered rates collection |

### Automation Example

```yaml
- trigger:
  - platform: event
    event_type: octopus_energy_electricity_next_day_rates
  condition: []
  action:
  - service: persistent_notification.create
    data:
      title: "Rates Updated"
      message: >
        New rates available for {{ trigger.event.data.mpan }}. Starting value is {{ trigger.event.data.rates[0]["value_inc_vat"] }}
```

## Electricity Previous Consumption Rates

`octopus_energy_electricity_previous_consumption_rates`

This is fired when the [previous consumption's](./entities/electricity.md#previous-accumulative-consumption) rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the previous consumption |
| `tariff_code` | `string` | The tariff code associated with previous consumption's rates |
| `mpan` | `string` | The mpan of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |
| `min_rate` | `float` | The minimum/lowest rate in the discovered rates collection |
| `max_rate` | `float` | The maximum/highest rate in the discovered rates collection |
| `average_rate` | `float` | The average rate in the discovered rates collection |

### Automation Example

```yaml
- trigger:
  - platform: event
    event_type: octopus_energy_electricity_previous_consumption_rates
  condition: []
  action:
  - service: persistent_notification.create
    data:
      title: "Rates Updated"
      message: >
        New rates available for {{ trigger.event.data.mpan }}. Starting value is {{ trigger.event.data.rates[0]["value_inc_vat"] }}
```

## Electricity Previous Consumption Override Rates

`octopus_energy_electricity_previous_consumption_override_rates`

This is fired when the [previous consumption override's](./entities/electricity.md#tariff-overrides) rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the previous consumption override |
| `tariff_code` | `string` | The tariff code associated with previous consumption override's rates |
| `mpan` | `string` | The mpan of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |

### Automation Example

```yaml
- trigger:
  - platform: event
    event_type: octopus_energy_electricity_previous_consumption_override_rates
  condition: []
  action:
  - service: persistent_notification.create
    data:
      title: "Rates Updated"
      message: >
        New rates available for {{ trigger.event.data.mpan }}. Starting value is {{ trigger.event.data.rates[0]["value_inc_vat"] }}
```

## Gas Current Day Rates

`octopus_energy_gas_current_day_rates`

This is fired when the current day rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the current day |
| `tariff_code` | `string` | The tariff code associated with current day's rates |
| `mprn` | `string` | The mprn of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |
| `min_rate` | `float` | The minimum/lowest rate in the discovered rates collection |
| `max_rate` | `float` | The maximum/highest rate in the discovered rates collection |
| `average_rate` | `float` | The average rate in the discovered rates collection |

### Automation Example

```yaml
- trigger:
  - platform: event
    event_type: octopus_energy_gas_current_day_rates
  condition: []
  action:
  - service: persistent_notification.create
    data:
      title: "Rates Updated"
      message: >
        New rates available for {{ trigger.event.data.mprn }}. Starting value is {{ trigger.event.data.rates[0]["value_inc_vat"] }}
```

## Gas Previous Day Rates

`octopus_energy_gas_previous_day_rates`

This is fired when the previous day rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the previous day |
| `tariff_code` | `string` | The tariff code associated with previous day's rates |
| `mprn` | `string` | The mprn of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |
| `min_rate` | `float` | The minimum/lowest rate in the discovered rates collection |
| `max_rate` | `float` | The maximum/highest rate in the discovered rates collection |
| `average_rate` | `float` | The average rate in the discovered rates collection |

### Automation Example

```yaml
- trigger:
  - platform: event
    event_type: octopus_energy_gas_previous_day_rates
  condition: []
  action:
  - service: persistent_notification.create
    data:
      title: "Rates Updated"
      message: >
        New rates available for {{ trigger.event.data.mprn }}. Starting value is {{ trigger.event.data.rates[0]["value_inc_vat"] }}
```

## Gas Next Day Rates

`octopus_energy_gas_next_day_rates`

This is fired when the next day rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the next day |
| `tariff_code` | `string` | The tariff code associated with next day's rates |
| `mprn` | `string` | The mprn of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |
| `min_rate` | `float` | The minimum/lowest rate in the discovered rates collection |
| `max_rate` | `float` | The maximum/highest rate in the discovered rates collection |
| `average_rate` | `float` | The average rate in the discovered rates collection |

### Automation Example

```yaml
- trigger:
  - platform: event
    event_type: octopus_energy_gas_next_day_rates
  condition: []
  action:
  - service: persistent_notification.create
    data:
      title: "Rates Updated"
      message: >
        New rates available for {{ trigger.event.data.mprn }}. Starting value is {{ trigger.event.data.rates[0]["value_inc_vat"] }}
```

## Gas Previous Consumption Rates

`octopus_energy_gas_previous_consumption_rates`

This is fired when the [previous consumption's](./entities/gas.md#previous-accumulative-consumption) rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the previous consumption |
| `tariff_code` | `string` | The tariff code associated with previous consumption's rates |
| `mprn` | `string` | The mprn of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |
| `min_rate` | `float` | The minimum/lowest rate in the discovered rates collection |
| `max_rate` | `float` | The maximum/highest rate in the discovered rates collection |
| `average_rate` | `float` | The average rate in the discovered rates collection |

### Automation Example

```yaml
- trigger:
  - platform: event
    event_type: octopus_energy_gas_previous_consumption_rates
  condition: []
  action:
  - service: persistent_notification.create
    data:
      title: "Rates Updated"
      message: >
        New rates available for {{ trigger.event.data.mprn }}. Starting value is {{ trigger.event.data.rates[0]["value_inc_vat"] }}
```

## Gas Previous Consumption Override Rates

`octopus_energy_gas_previous_consumption_override_rates`

This is fired when the [previous consumption override's](./entities/gas.md#tariff-overrides) rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the previous consumption override |
| `tariff_code` | `string` | The tariff code associated with previous consumption override's rates |
| `mprn` | `string` | The mprn of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |

### Automation Example

```yaml
- trigger:
  - platform: event
    event_type: octopus_energy_gas_previous_consumption_override_rates
  condition: []
  action:
  - service: persistent_notification.create
    data:
      title: "Rates Updated"
      message: >
        New rates available for {{ trigger.event.data.mprn }}. Starting value is {{ trigger.event.data.rates[0]["value_inc_vat"] }}
```

## New Saving Session

`octopus_energy_new_octoplus_saving_session`

This event is raised when a new saving session is discovered.

| Attribute | Type | Description |
|-----------|------|-------------|
| `account_id` | `string` | The id of the account the new saving session is for |
| `event_code` | `string` | The code of the new saving session event. This is required if you wishing to use the [join event service](./services.md#join_octoplus_saving_session_event) |
| `event_id` | `string` | The id of the event |
| `event_start` | `datetime` | The date/time the event starts |
| `event_end` | `datetime` | The date/time the event ends |
| `event_octopoints_per_kwh` | `integer` | The number of octopoints that are awarded per kwh saved during the event |

### Automation Example

```yaml
- trigger:
  - platform: event
    event_type: octopus_energy_new_octoplus_saving_session
  condition: []
  action:
  - service: persistent_notification.create
    data:
      title: "New Saving Session"
      message: >
        New Octopus Energy saving session available. It starts at {{ trigger.event.data["event_start"].strftime('%H:%M') }} on {{ trigger.event.data["event_start"].day }}/{{ trigger.event.data["event_start"].month }}
```

## All Saving Sessions

`octopus_energy_all_octoplus_saving_sessions`

This event is raised when saving sessions are refreshed and contain all available and joined events.

| Attribute | Type | Description |
|-----------|------|-------------|
| `account_id` | `string` | The id of the account the saving session events are for |
| `available_events` | `array` | The collection of saving session events that you haven't joined |
| `joined_events` | `array` | The collection of saving session events that you have joined. This will include upcoming and past events |

Each available event item will include the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `integer` | The id of the event |
| `code` | `string` | The event code of the event. This will be required to join via the [join service](./services.md) |
| `start` | `datetime` | The date/time the event starts |
| `end` | `datetime` | The date/time the event starts |
| `octopoints_per_kwh` | `integer` | The number of octopoints that are awarded per kwh saved during the event |

Each joined event item will include the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `integer` | The id of the event |
| `start` | `datetime` | The date/time the event starts |
| `end` | `datetime` | The date/time the event starts |
| `octopoints_per_kwh` | `integer` | The number of octopoints that are awarded per kwh saved during the event |
| `rewarded_octopoints` | `integer` | The total number of octopoints that were awarded (if any or known) |

### Automation Example

```yaml
- trigger:
  - platform: event
    event_type: octopus_energy_all_octoplus_saving_sessions
  condition: []
  action:
  - service: persistent_notification.create
    data:
      title: "Saving Sessions Updated"
      message: >
        Saving session events updated. The latest joined event awarded {{ trigger.event.data.joined_events[0]["rewarded_octopoints"] }}
```