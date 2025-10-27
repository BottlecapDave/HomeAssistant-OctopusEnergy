# Greenness Forecast

To support the [greener nights](https://octopus.energy/smart/greener-nights/) supported by Octopus Energy, the following entities are provided.

## Current Index

`sensor.octopus_energy_{{ACCOUNT_ID}}_greenness_forecast_current_index`

The greenness index for the current period.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

!!! info
    If you are wanting a nice way to display the upcoming forecast, then why not try a [community card](../community.md#greenness-forecast)?

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

For each forecast item, the following attributes are provided

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The time the current forecast period started |
| `end` | `datetime` | The time the current forecast period ends |
| `greenness_index` | `int` | The index for the current forecast |
| `greenness_score` | `string` | The score associated by Octopus Energy for the current forecast |
| `is_highlighted` | `bool` | Determines if the current forecast has been highlighted by Octopus Energy |

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#greenness-forecast-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

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

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#greenness-forecast-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

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

For `current`, the following attributes are provided

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The time the current forecast period started |
| `end` | `datetime` | The time the current forecast period ends |
| `greenness_index` | `int` | The index for the current forecast |
| `greenness_score` | `string` | The score associated by Octopus Energy for the current forecast |
| `is_highlighted` | `bool` | Determines if the current forecast has been highlighted by Octopus Energy |

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#greenness-forecast-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.