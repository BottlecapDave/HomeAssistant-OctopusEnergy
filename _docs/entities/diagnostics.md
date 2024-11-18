# Diagnostic Entities

These entities can help diagnose issues.

## Account Data Last Retrieved

`sensor.octopus_energy_{{ACCOUNT_ID}}_account_data_last_retrieved`

This sensor states when account data was last retrieved.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `attempts` | `integer` | The number of attempts that have been made to retrieve the data |
| `next_refresh` | `datetime` | The timestamp of when the data will next be attempted to be retrieved |
| `last_error` | `string` | The error that was raised to cause the last retrieval attempt to fail |

## Current Consumption Data Last Retrieved

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_consumption_data_last_retrieved` or `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_consumption_data_last_retrieved`

This sensor states when the home mini current consumption data was last retrieved.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `attempts` | `integer` | The number of attempts that have been made to retrieve the data |
| `next_refresh` | `datetime` | The timestamp of when the data will next be attempted to be retrieved |
| `last_error` | `string` | The error that was raised to cause the last retrieval attempt to fail |

## Current Consumption Home Pro Data Last Retrieved

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_home_pro_current_consumption_data_last_retrieved` or `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_home_pro_current_consumption_data_last_retrieved`

This sensor states when the home pro current consumption data was last retrieved.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `attempts` | `integer` | The number of attempts that have been made to retrieve the data |
| `next_refresh` | `datetime` | The timestamp of when the data will next be attempted to be retrieved |
| `last_error` | `string` | The error that was raised to cause the last retrieval attempt to fail |

## Greenness Forecast Data Last Retrieved

`sensor.octopus_energy_{{ACCOUNT_ID}}_greenness_forecast_data_last_retrieved`

This sensor states when greenness forecast data was last retrieved.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `attempts` | `integer` | The number of attempts that have been made to retrieve the data |
| `next_refresh` | `datetime` | The timestamp of when the data will next be attempted to be retrieved |
| `last_error` | `string` | The error that was raised to cause the last retrieval attempt to fail |

## Intelligent Dispatches Data Last Retrieved

`sensor.octopus_energy_{{ACCOUNT_ID}}_intelligent_dispatches_data_last_retrieved`

This sensor states when intelligent dispatches data was last retrieved.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `attempts` | `integer` | The number of attempts that have been made to retrieve the data |
| `next_refresh` | `datetime` | The timestamp of when the data will next be attempted to be retrieved |
| `last_error` | `string` | The error that was raised to cause the last retrieval attempt to fail |

## Intelligent Settings Data Last Retrieved

`sensor.octopus_energy_{{ACCOUNT_ID}}_intelligent_settings_data_last_retrieved`

This sensor states when intelligent settings data was last retrieved.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `attempts` | `integer` | The number of attempts that have been made to retrieve the data |
| `next_refresh` | `datetime` | The timestamp of when the data will next be attempted to be retrieved |
| `last_error` | `string` | The error that was raised to cause the last retrieval attempt to fail |

## Previous Consumption And Rates Data Last Retrieved

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_consumption_and_rates_data_last_retrieved` or `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_consumption_and_rates_data_last_retrieved`

This sensor states when the previous consumption and associated rate data was last retrieved.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `attempts` | `integer` | The number of attempts that have been made to retrieve the data |
| `next_refresh` | `datetime` | The timestamp of when the data will next be attempted to be retrieved |
| `last_error` | `string` | The error that was raised to cause the last retrieval attempt to fail |

## Rates Data Last Retrieved

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_rates_data_last_retrieved` or `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_rates_data_last_retrieved`

This sensor states when the previous/current and next rate data was last retrieved.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `attempts` | `integer` | The number of attempts that have been made to retrieve the data |
| `next_refresh` | `datetime` | The timestamp of when the data will next be attempted to be retrieved |
| `last_error` | `string` | The error that was raised to cause the last retrieval attempt to fail |

## Saving Sessions Data Last Retrieved

`sensor.octopus_energy_{{ACCOUNT_ID}}_saving_sessions_data_last_retrieved`

This sensor states when saving sessions data was last retrieved.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `attempts` | `integer` | The number of attempts that have been made to retrieve the data |
| `next_refresh` | `datetime` | The timestamp of when the data will next be attempted to be retrieved |
| `last_error` | `string` | The error that was raised to cause the last retrieval attempt to fail |

## Free Electricity Sessions Data Last Retrieved

`sensor.octopus_energy_{{ACCOUNT_ID}}_free_electricity_sessions_data_last_retrieved`

This sensor states when free electricity sessions data was last retrieved.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `attempts` | `integer` | The number of attempts that have been made to retrieve the data |
| `next_refresh` | `datetime` | The timestamp of when the data will next be attempted to be retrieved |
| `last_error` | `string` | The error that was raised to cause the last retrieval attempt to fail |

## Standing Charge Data Last Retrieved

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_standing_charge_data_last_retrieved` or `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_standing_charge_data_last_retrieved`

This sensor states when the standing charge data was last retrieved.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `attempts` | `integer` | The number of attempts that have been made to retrieve the data |
| `next_refresh` | `datetime` | The timestamp of when the data will next be attempted to be retrieved |
| `last_error` | `string` | The error that was raised to cause the last retrieval attempt to fail |

## Wheel Of Fortune Data Last Retrieved

`sensor.octopus_energy_{{ACCOUNT_ID}}_wheel_of_fortune_data_last_retrieved`

This sensor states when wheel of fortune data was last retrieved.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `attempts` | `integer` | The number of attempts that have been made to retrieve the data |
| `next_refresh` | `datetime` | The timestamp of when the data will next be attempted to be retrieved |
| `last_error` | `string` | The error that was raised to cause the last retrieval attempt to fail |