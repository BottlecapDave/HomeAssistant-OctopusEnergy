# Fan Club

The following entities are available if you are a member of the [Octopus Energy Fan Club](https://www.octopusenergygeneration.com/fan-club/).

## Current Discount

`sensor.octopus_energy_fan_club_{{ACCOUNT_ID}}_{{FAN_CLUB_ID}}_current_discount`

The current discount applied for the specified fan club.

This is in pounds and pence (e.g. 1.01 = £1.01).

| Attribute | Type | Description |
|-----------|------|-------------|
| `source` | `string` | The source of the discount |
| `start` | `datetime` | The date/time when the discount started |
| `end` | `datetime` | The date/time when the discount ends |
| `current_day_min_discount` | `float` | The minimum discount available for the current day |
| `current_day_max_discount` | `float` | The maximum discount available for the current day |
| `current_day_average_discount` | `float` | The average discount for the current day |

## Previous Discount

`sensor.octopus_energy_fan_club_{{ACCOUNT_ID}}_{{FAN_CLUB_ID}}_previous_discount`

The previous discount for the specified fan club, that differs from the current discount. If there is no previous discount (e.g. discounts before now are of the same value as the current discount), then this will be reported as `unknown`/`none`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `source` | `string` | The source of the discount |
| `start` | `datetime` | The date/time when the discount started |
| `end` | `datetime` | The date/time when the discount ended |

## Next Discount

`sensor.octopus_energy_fan_club_{{ACCOUNT_ID}}_{{FAN_CLUB_ID}}_next_discount`

The next discount for the specified fan club, that differs from the current discount. If there is no next discount (e.g. discounts after now are of the same value as the current discount), then this will be reported as `unknown`/`none`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `source` | `string` | The source of the discount |
| `start` | `datetime` | The date/time when the discount starts |
| `end` | `datetime` | The date/time when the discount ends |

## Discounts

`event.octopus_energy_fan_club_{{ACCOUNT_ID}}_{{FAN_CLUB_ID}}_discounts`

The state of this sensor states when the discounts were last retrieved. The attributes of this sensor exposes the available discounts for a given fan club source.

| Attribute | Type | Description |
|-----------|------|-------------|
| `discounts` | `array` | The list of past, present and future discounts |
| `account_id` | `string` | The id of the account the discounts are for |
| `source` | `string` | The source of the discounts (e.g. Fan #1) |

Each rate item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the discount starts/started |
| `end` | `datetime` | The date/time when the discount ends/ended |
| `discount` | `float` | The value of the discount |
| `is_estimated` | `boolean` | Determines if the discount is estimated |