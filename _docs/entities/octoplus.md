# Octoplus

To support Octopus Energy's [octoplus programme](https://octopus.energy/octoplus/), the following entities are available

## Octoplus Points

`sensor.octopus_energy_{{ACCOUNT_ID}}_octoplus_points`

Determines the current Octoplus points balance. This sensor will only be available if you have enrolled on the octoplus programme. 

| Attribute | Type | Description |
|-----------|------|-------------|
| `redeemable_points` | `integer` | The number of points that can be redeemed into account credit |
| `data_last_retrieved` | `datetime` | The date/time the underlying data was last retrieved from Octopus Energy APIs |

## Saving Sessions

`binary_sensor.octopus_energy_{{ACCOUNT_ID}}_octoplus_saving_sessions`

Binary sensor to indicate if a saving session that the account has joined is active.

| Attribute | Type | Description |
|-----------|------|-------------|
| `current_joined_event_start` | `datetime` | The datetime the current saving session started |
| `current_joined_event_end` | `datetime` | The datetime the current saving session will end |
| `current_joined_event_duration_in_minutes` | `float` | The duration in minutes of the current saving session |
| `next_joined_event_start` | `datetime` | The datetime the next saving session will start |
| `next_joined_event_end` | `datetime` | The datetime the next saving session will end |
| `next_joined_event_duration_in_minutes` | `float` | The duration in minutes of the next saving session |

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#saving-sessions-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

## Saving Session Events

`event.octopus_energy_{{ACCOUNT_ID}}_octoplus_saving_session_events`

The state of this sensor states when the saving session events were last updated. The attributes of this sensor exposes the joined and available saving sessions.

| Attribute | Type | Description |
|-----------|------|-------------|
| `available_events` | `array` | The collection of saving session events that you haven't joined |
| `joined_events` | `array` | The collection of saving session events that you have joined. This will include upcoming and past events |

Each available event item will include the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `integer` | The id of the event |
| `code` | `string` | The event code of the event. This will be required to join via the [join service](../services.md) |
| `start` | `datetime` | The date/time the event starts |
| `end` | `datetime` | The date/time the event starts |
| `duration_in_minutes` | `integer` | The duration of the event in minutes |
| `octopoints_per_kwh` | `integer` | The number of octopoints that are awarded per kwh saved during the event |

Each joined event item will include the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `integer` | The id of the event |
| `start` | `datetime` | The date/time the event starts |
| `end` | `datetime` | The date/time the event starts |
| `duration_in_minutes` | `integer` | The duration of the event in minutes |
| `rewarded_octopoints` | `integer` | The total number of octopoints that were awarded (if any or known) |
| `octopoints_per_kwh` | `integer` | The number of octopoints that are/were awarded per kwh saved during the event (if known) |

## Saving Session Baseline

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_octoplus_saving_session_baseline`

This will indicate the baseline consumption that you need to be below for the current 30 minute period of the current saving session or the first 30 minute period of the next saving session. 

You can use the [current period consumption](./electricity.md#current-interval-accumulative-consumption) sensor (if available) to see how on track you are.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

!!! info

    An export variant of this sensor exists for export based meters.

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The start datetime the current baseline applies |
| `end` | `datetime` | The end datetime the current baseline applies |
| `is_incomplete_calculation` | `bool` | Determines if the calculation is based on the full set or partial set of data |
| `consumption_items` | `list` | The consumption that was used to calculate the baselines |
| `total_baseline` | `float` | The total baseline for the current saving session |
| `baselines` | `list` | The collection of baselines for the current saving session |

Each item within `consumption_items` consists of the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The start datetime the consumption period |
| `end` | `datetime` | The end datetime the consumption period |
| `consumption` | `float` | The total consumption within the period in kWh |

Each item within `baselines` consists of the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The start datetime the baseline period |
| `end` | `datetime` | The end datetime the baseline period |
| `baseline` | `float` | The consumption in kWh for the baseline period |
| `is_incomplete_calculation` | `bool` | Determines if the calculation is based on the full set or partial set of data |

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#saving-sessions-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

## Free Electricity Sessions

`binary_sensor.octopus_energy_{{ACCOUNT_ID}}_octoplus_free_electricity_session`

Binary sensor to indicate if a free electricity session is active.

!!! warning

    This sensor uses public information. However it is only applicable to your account if you have joined Octoplus and have signed up to [free electricity sessions](https://octopus.energy/free-electricity/)

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `current_event_start` | `datetime` | The datetime the current free electricity session started |
| `current_event_end` | `datetime` | The datetime the current free electricity session will end |
| `current_event_duration_in_minutes` | `float` | The duration in minutes of the current free electricity session |
| `next_event_start` | `datetime` | The datetime the next free electricity session will start |
| `next_event_end` | `datetime` | The datetime the next free electricity session will end |
| `next_event_duration_in_minutes` | `float` | The duration in minutes of the next free electricity session |

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#free-electricity-sessions-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

## Free Electricity Session Events

`event.octopus_energy_{{ACCOUNT_ID}}_octoplus_free_electricity_session_events`

The state of this sensor states when the free electricity session events were last updated. The attributes of this sensor exposes the past, present and future free electricity sessions.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `events` | `array` | The collection of free electricity events |

Each item in the `events` attribute will include the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `code` | `string` | The code of the event. |
| `start` | `datetime` | The date/time the event starts |
| `end` | `datetime` | The date/time the event starts |
| `duration_in_minutes` | `integer` | The duration of the event in minutes |

## Free Electricity Session Baseline

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_octoplus_free_electricity_session_baseline`

This will indicate the baseline consumption that you need to be above for the current 30 minute period of the current free electricity session or the first 30 minute period of the next free electricity session. 

You can use the [current period consumption](./electricity.md#current-interval-accumulative-consumption) sensor (if available) to see how on track you are.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

!!! info

    An export variant of this sensor exists for export based meters.

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The start datetime the current baseline applies |
| `end` | `datetime` | The end datetime the current baseline applies |
| `is_incomplete_calculation` | `bool` | Determines if the calculation is based on the full set or partial set of data |
| `consumption_items` | `list` | The consumption that was used to calculate the baselines |
| `total_baseline` | `float` | The total baseline for the current saving session |
| `baselines` | `list` | The collection of baselines for the current saving session |

Each item within `consumption_items` consists of the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The start datetime the consumption period |
| `end` | `datetime` | The end datetime the consumption period |
| `consumption` | `float` | The total consumption within the period in kWh |

Each item within `baselines` consists of the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The start datetime the baseline period |
| `end` | `datetime` | The end datetime the baseline period |
| `baseline` | `float` | The consumption in kWh for the baseline period |
| `is_incomplete_calculation` | `bool` | Determines if the calculation is based on the full set or partial set of data |

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#free-electricity-sessions-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

## Services

There are some services available relating to these entities that you might find useful. They can be found in the [services docs](../services.md).

