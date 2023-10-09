# Events

- [Events](#events)
  - [Electricity Current Day Rates](#electricity-current-day-rates)
  - [Electricity Previous Day Rates](#electricity-previous-day-rates)
  - [Electricity Next Day Rates](#electricity-next-day-rates)
  - [Electricity Previous Consumption Rates](#electricity-previous-consumption-rates)
  - [Electricity Previous Consumption Override Rates](#electricity-previous-consumption-override-rates)
  - [Gas Current Day Rates](#gas-current-day-rates)
  - [Gas Previous Day Rates](#gas-previous-day-rates)
  - [Gas Next Day Rates](#gas-next-day-rates)
  - [Gas Previous Consumption Rates](#gas-previous-consumption-rates)
  - [Gas Previous Consumption Override Rates](#gas-previous-consumption-override-rates)

The following events are raised by the integration. These events power various entities mentioned above. They can also be used to trigger automations. An example automation might look like the following

```yaml
- alias: OE rates change
  trigger:
  - platform: event
    event_type: octopus_energy_electricity_next_day_rates
  condition: []
  action:
  - event: notify_channels
    event_data_template:
      mode: message
      title: OE price changes
      message: >
        New rates available for {{ trigger.event.data.mpan }}. Starting value is {{ trigger.event.data.rates[0]["value_inc_vat"] }}
      target: <@ULU7111GU>
      length_hint: 00:00:04
```

## Electricity Current Day Rates

`octopus_energy_electricity_current_day_rates`

This is fired when the current day rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the current day |
| `tariff_code` | `string` | The tariff code associated with current day's rates |
| `mpan` | `string` | The mpan of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |

## Electricity Previous Day Rates

`octopus_energy_electricity_previous_day_rates`

This is fired when the previous day rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the previous day |
| `tariff_code` | `string` | The tariff code associated with previous day's rates |
| `mpan` | `string` | The mpan of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |

## Electricity Next Day Rates

`octopus_energy_electricity_next_day_rates`

This is fired when the next day rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the next day |
| `tariff_code` | `string` | The tariff code associated with next day's rates |
| `mpan` | `string` | The mpan of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |

## Electricity Previous Consumption Rates

`octopus_energy_electricity_previous_consumption_rates`

This is fired when the [previous consumption's](./entities/electricity.md#previous-accumulative-consumption) rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the previous consumption |
| `tariff_code` | `string` | The tariff code associated with previous consumption's rates |
| `mpan` | `string` | The mpan of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |

## Electricity Previous Consumption Override Rates

`octopus_energy_electricity_previous_consumption_override_rates`

This is fired when the [previous consumption override's](./entities/electricity.md#tariff-overrides) rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the previous consumption override |
| `tariff_code` | `string` | The tariff code associated with previous consumption override's rates |
| `mpan` | `string` | The mpan of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |

## Gas Current Day Rates

`octopus_energy_gas_current_day_rates`

This is fired when the current day rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the current day |
| `tariff_code` | `string` | The tariff code associated with current day's rates |
| `mprn` | `string` | The mprn of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |

## Gas Previous Day Rates

`octopus_energy_gas_previous_day_rates`

This is fired when the previous day rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the previous day |
| `tariff_code` | `string` | The tariff code associated with previous day's rates |
| `mprn` | `string` | The mprn of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |

## Gas Next Day Rates

`octopus_energy_gas_next_day_rates`

This is fired when the next day rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the next day |
| `tariff_code` | `string` | The tariff code associated with next day's rates |
| `mprn` | `string` | The mprn of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |

## Gas Previous Consumption Rates

`octopus_energy_gas_previous_consumption_rates`

This is fired when the [previous consumption's](./entities/gas.md#previous-accumulative-consumption) rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the previous consumption |
| `tariff_code` | `string` | The tariff code associated with previous consumption's rates |
| `mprn` | `string` | The mprn of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |

## Gas Previous Consumption Override Rates

`octopus_energy_gas_previous_consumption_override_rates`

This is fired when the [previous consumption override's](./entities/gas.md#tariff-overrides) rates are updated.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the previous consumption override |
| `tariff_code` | `string` | The tariff code associated with previous consumption override's rates |
| `mprn` | `string` | The mprn of the meter associated with these rates |
| `serial_number` | `string` | The serial number of the meter associated with these rates |