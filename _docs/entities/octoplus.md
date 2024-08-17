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

Binary sensor to indicate if a saving session that the account has joined is active. Also supplies the list of joined events including future events.

| Attribute | Type | Description |
|-----------|------|-------------|
| `current_joined_event_start` | `datetime` | The datetime the current saving session started |
| `current_joined_event_end` | `datetime` | The datetime the current saving session will end |
| `current_joined_event_duration_in_minutes` | `float` | The duration in minutes of the current saving session |
| `next_joined_event_start` | `datetime` | The datetime the next saving session will start |
| `next_joined_event_end` | `datetime` | The datetime the next saving session will end |
| `next_joined_event_duration_in_minutes` | `float` | The duration in minutes of the next saving session |
| `data_last_retrieved` | `datetime` | The date/time the underlying data was last retrieved from Octopus Energy APIs |

## Saving Session Events

`event.octopus_energy_{{ACCOUNT_ID}}_octoplus_saving_session_events`

The state of this sensor states when the saving session events were last updated. The attributes of this sensor exposes the current day's rates.

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

## Services

There are some services available relating to these entities that you might find useful. They can be found in the [services docs](../services.md).

