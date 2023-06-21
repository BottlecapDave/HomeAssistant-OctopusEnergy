# Gas Sensors

You'll get the following sensors for each gas meter with an active agreement:

- [Gas Sensors](#gas-sensors)
  - [Current Rate](#current-rate)
  - [Smart Meter Sensors](#smart-meter-sensors)
  - [Previous Accumulative Consumption](#previous-accumulative-consumption)
  - [Previous Accumulative Consumption (kWH)](#previous-accumulative-consumption-kwh)
  - [Previous Accumulative Cost](#previous-accumulative-cost)
  - [Home Mini Sensors](#home-mini-sensors)
    - [Current Consumption (Gas)](#current-consumption-gas)
  - [Tariff Overrides](#tariff-overrides)
    - [Previous Accumulative Cost Override Tariff (Gas)](#previous-accumulative-cost-override-tariff-gas)
    - [Previous Accumulative Cost Override (Gas)](#previous-accumulative-cost-override-gas)

## Current Rate

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_rate`

The rate of the current day that gas consumption is charged at (including VAT).

| Attribute | Type | Description |
|-----------|------|-------------|
| `value_inc_vat` | `float` | The value of the price including VAT |
| `valid_from` | `datetime` | The date/time when the price is valid from |
| `valid_to` | `datetime` | The date/time when the price is valid to |
| `tariff_code` | `string` | The tariff code the current price was defined by |
| `is_capped` | `boolean` | Determines if the price has been capped by the cap set when you setup your account |

## Smart Meter Sensors

If your account information doesn't determine you have a smart meter, then you will have the following sensors in a disabled state. If you enable these sensors, they might not work correctly in this scenario. 

If you are wishing to use these sensors with the Energy Dashboard, then you can follow this [guide](../energy_dashboard.md).

> By default, it's not possible to include current consumption sensors. This is due to Octopus Energy only receive data from the smart meters up to the previous day.

## Previous Accumulative Consumption

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption`

The total consumption reported by the meter for the previous day in m3. If your meter reports in m3, then this will be an accurate value reported by Octopus, otherwise it will be a calculated/estimated value.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mprn` | `string` | The mprn for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_estimated` | `boolean` | Determines if the consumption was estimated. This can occur if your meter reports in `kwh`. |
| `total_kwh` | `float` | The total energy value for the previous day in `kwh`. If your meter reports in `m3`, then this will be estimated using your set [calorific value](../setup_account.md#calorific-value) |
| `total_m3` | `float` | The total energy value for the previous day in `m3`. If your meter reports in `kwh`, then this will be estimated using your set [calorific value](../setup_account.md#calorific-value) |
| `last_calculated_timestamp` | `datetime` | The timestamp determining when the consumption was last calculated. |
| `charges` | `array` | Collection of consumption periods for the previous day broken down into 30 minute periods. |
| `calorific_value` | `float` | The calorific value used for the calculations, as set in your [account](../setup_account.md#calorific-value). |

## Previous Accumulative Consumption (kWH)

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption_kwh`

The total consumption reported by the meter for the previous day in kwh. If your meter reports in kwh, then this will be an accurate value reported by Octopus, otherwise it will be a calculated/estimated value.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mprn` | `string` | The mprn for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_estimated` | `boolean` | Determines if the consumption was estimated. This can occur if your meter reports in `m3`. |
| `last_calculated_timestamp` | `datetime` | The timestamp determining when the consumption was last calculated. |
| `charges` | `array` | Collection of consumption periods for the previous day broken down into 30 minute periods. |
| `calorific_value` | `float` | The calorific value used for the calculations, as set in your [account](../setup_account.md#calorific-value). |

## Previous Accumulative Cost

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_cost`

The total cost for the previous day, including the standing charge.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mprn` | `string` | The mprn for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `tariff_code` | `string` | The tariff that determined the cost |
| `standing_charge` | `float` | The standing charge included in the cost |
| `total_without_standing_charge` | `float` | The total cost of the previous day excluding the standing charge |
| `total` | `float` | The total cost for the previous day |
| `charges` | `array` | Collection of consumption periods and costs for the previous day broken down into 30 minute periods. |
| `last_calculated_timestamp` | `datetime` | The timestamp determining when the cost was last calculated. |
| `calorific_value` | `float` | The calorific value used for the calculations, as set in your [account](../setup_account.md#calorific-value). |

## Home Mini Sensors

### Current Consumption (Gas)

> This will only be available if you have specified you have a [Octopus Home Mini](../setup_account.md#home-mini). Do not set unless you have one

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_consumption`

The latest gas consumption sent to Octopus Energy. By default, this will update every minute. This has been built to see the accumulation within the energy dashboard. If you are wanting a sensor to see the current day's accumulation, then you will need to use something like [utility meter](https://www.home-assistant.io/integrations/utility_meter/). It has been noticed that daily consumption reported in Home Assistant can differ to when looking at past data within Octopus Energy. It looks like this is because Octopus Energy will favour "official" data from your smart meter over the data they collect.

If current consumption data is unable to be retrieved, then the integration will attempt to retrieve missing data. This will be done up to 5 days behind to give a buffer before the API requires a higher interval and will not be changed.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mprn` | `string` | The mprn for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |

## Tariff Overrides

You may be on an existing tariff but want to know if the grass is greener (or cheaper) on the other side. The following entities are available in a disabled state, which when enabled can give you an indication what you'd be paying if you were on a different tariff and didn't change your energy habits. 

Instructions on how to find tariffs can be found in the [faq](../faq.md#i-want-to-use-the-tariff-overrides-but-how-do-i-find-an-available-tariff).

> Please note: When updating the tariff depending on what previous consumption data is available, it can take up to 24 hours to update the cost. This will be improved in the future.

### Previous Accumulative Cost Override Tariff (Gas)

`text.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_cost_override_tariff`

This is used to define the gas tariff you want to compare

### Previous Accumulative Cost Override (Gas)

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_cost_override`

This is the cost of the previous gas accumulation based on the specified tariff override.

For attributes, see [Previous Accumulative Cost](#previous-accumulative-cost).