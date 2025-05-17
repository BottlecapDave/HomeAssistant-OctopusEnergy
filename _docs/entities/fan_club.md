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