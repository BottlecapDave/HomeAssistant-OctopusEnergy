# Greenness Forecast

To support the [greenness forecast](https://octopus.energy/smart/greener-days/) supported by Octopus Energy, the following entities are provided.

## Current Index

`sensor.octopus_energy_{{ACCOUNT_ID}}_greenness_forecast_current_index`

The greenness index for the current period.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The time the current forecast period started |
| `end` | `datetime` | The time the current forecast period ends |
| `greenness_index` | `int` | The index for the current forecast |
| `greenness_score` | `string` | The score associated by Octopus Energy for the current forecast |
| `is_highlighted` | `bool` | Determines if the current forecast has been highlighted by Octopus Energy |
| `next_start` | `datetime` | The time the next forecast period starts |
| `next_end` | `datetime` | The time the next forecast period ends |
| `forecast` | `array` | The entire upcoming forecast |
| `data_last_retrieved` | `datetime` | The date/time the underlying data was last retrieved from Octopus Energy APIs |

For each forecast item, the following attributes are provided

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The time the current forecast period started |
| `end` | `datetime` | The time the current forecast period ends |
| `greenness_index` | `int` | The index for the current forecast |
| `greenness_score` | `string` | The score associated by Octopus Energy for the current forecast |
| `is_highlighted` | `bool` | Determines if the current forecast has been highlighted by Octopus Energy |

## Next Index

`sensor.octopus_energy_{{ACCOUNT_ID}}_greenness_forecast_next_index`

The greenness index for the next period.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The time the next forecast period started |
| `end` | `datetime` | The time the next forecast period ends |
| `greenness_index` | `int` | The index for the next forecast |
| `greenness_score` | `string` | The score associated by Octopus Energy for the next forecast |
| `is_highlighted` | `bool` | Determines if the next forecast has been highlighted by Octopus Energy |
| `data_last_retrieved` | `datetime` | The date/time the underlying data was last retrieved from Octopus Energy APIs |

## Highlighted

`binary_sensor.octopus_energy_{{ACCOUNT_ID}}_greenness_forecast_highlighted`

Determines if the current greenness forecast has been highlighted by OE as the greenest for the current forecast.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `current` | `object` | The details of the currently highlighted forecast |
| `next_start` | `datetime` | The time the next highlighted forecast period starts |
| `next_end` | `datetime` | The time the next highlighted forecast period ends |
| `data_last_retrieved` | `datetime` | The date/time the underlying data was last retrieved from Octopus Energy APIs |

For `current`, the following attributes are provided

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The time the current forecast period started |
| `end` | `datetime` | The time the current forecast period ends |
| `greenness_index` | `int` | The index for the current forecast |
| `greenness_score` | `string` | The score associated by Octopus Energy for the current forecast |
| `is_highlighted` | `bool` | Determines if the current forecast has been highlighted by Octopus Energy |