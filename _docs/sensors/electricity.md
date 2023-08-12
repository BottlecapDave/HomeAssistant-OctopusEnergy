# Electricity Sensors

You'll get the following sensors for each electricity meter with an active agreement.

- [Electricity Sensors](#electricity-sensors)
  - [Current Rate](#current-rate)
  - [Previous Rate](#previous-rate)
  - [Next rate](#next-rate)
  - [Smart Meter Sensors](#smart-meter-sensors)
    - [Previous Accumulative Consumption](#previous-accumulative-consumption)
    - [Previous Accumulative Consumptions (Peak Rate)](#previous-accumulative-consumptions-peak-rate)
    - [Previous Accumulative Consumption (Off Peak Rate)](#previous-accumulative-consumption-off-peak-rate)
    - [Previous Accumulative Cost](#previous-accumulative-cost)
    - [Previous Accumulative Cost (Peak Rate)](#previous-accumulative-cost-peak-rate)
    - [Previous Accumulative Cost (Off Peak Rate)](#previous-accumulative-cost-off-peak-rate)
  - [Export Sensors](#export-sensors)
  - [Home Mini Sensors](#home-mini-sensors)
    - [Current Consumption](#current-consumption)
    - [Current Demand](#current-demand)
    - [Current Accumulative Consumption](#current-accumulative-consumption)
    - [Current Accumulative Consumptions (Peak Rate)](#current-accumulative-consumptions-peak-rate)
    - [Current Accumulative Consumption (Off Peak Rate)](#current-accumulative-consumption-off-peak-rate)
    - [Current Accumulative Cost](#current-accumulative-cost)
    - [Current Accumulative Cost (Peak Rate)](#current-accumulative-cost-peak-rate)
    - [Current Accumulative Cost (Off Peak Rate)](#current-accumulative-cost-off-peak-rate)
  - [Tariff Overrides](#tariff-overrides)
    - [Previous Accumulative Cost Override Tariff (Electricity)](#previous-accumulative-cost-override-tariff-electricity)
    - [Previous Accumulative Cost Override (Electricity)](#previous-accumulative-cost-override-electricity)

## Current Rate

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_rate`

The current rate that energy consumption is charged at (including VAT).

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `tariff` | `string` | The tariff the meter/rates are associated with |
| `all_rates` | `array` | Collection of latest rates for the previous day and next few days |
| `applicable_rates` | `array` | Collection of rates where the current rate applies, in case it spans multiple time periods. |
| `valid_from` | `datetime` | The date/time when the rate is valid from |
| `valid_to` | `datetime` | The date/time when the rate is valid to |
| `is_capped` | `boolean` | Determines if the rate has been capped by the cap set when you setup your account |
| `is_intelligent_adjusted` | `boolean` | Determines if the rate is the result of being adjusted for intelligent dispatches. This is only applicable for intelligent tariffs |
| `current_day_min_rate` | `float` | The minimum rate available for the current day |
| `current_day_max_rate` | `float` | The maximum rate available for the current day |
| `current_day_average_rate` | `float` | The average rate for the current day |
| `price_cap` | `float` | The price cap that has been configured for the account and is currently applied to all electricity rates |

## Previous Rate

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_rate`

The previous rate that energy consumption was charged at (including VAT). If there is no previous rate (e.g. rates before now are of the same value as the current rate), then this will be reported as `unknown`/`none`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `applicable_rates` | `array` | Collection of rates where the previous rate applies, in case it spans multiple time periods. |
| `valid_from` | `datetime` | The date/time when the rate is valid from |
| `valid_to` | `datetime` | The date/time when the rate is valid to |

## Next rate

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_next_rate`

The next/upcoming rate that energy consumption will be charged at (including VAT). If there is no next rate (e.g. rates after now are of the same value as the current rate), then this will be reported as `unknown`/`none`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `applicable_rates` | `array` | Collection of rates where the next rate applies, in case it spans multiple time periods. |
| `valid_from` | `datetime` | The date/time when the rate is valid from |
| `valid_to` | `datetime` | The date/time when the rate is valid to |

## Smart Meter Sensors

If your account information doesn't determine you have a smart meter, then you will have the following sensors in a disabled state. If you enable these sensors, they might not work correctly in this scenario.

If you are wishing to use these sensors with the Energy Dashboard, then you can follow this [guide](../energy_dashboard.md).

> By default, it's not possible to include current consumption sensors. This is due to Octopus Energy only receive data from the smart meters up to the previous day. If you want current consumption, then you will need a [Octopus Home Mini](https://octopus.energy/blog/octopus-home-mini/).

### Previous Accumulative Consumption

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption`

The total consumption reported by the meter for the previous day.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `total` | `float` | The total energy value for the previous day |
| `charges` | `array` | Collection of consumption periods for the previous day broken down into 30 minute periods. |

### Previous Accumulative Consumptions (Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption_peak`

The total consumption reported by the meter for the previous day that applied during peak hours. This is disabled by default. This will only be populated if you're on a tariff with two available rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

### Previous Accumulative Consumption (Off Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption_off_peak`

The total consumption reported by the meter for the previous day that applied during off peak hours. This is disabled by default. This will only be populated if you're on a tariff with two available rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

### Previous Accumulative Cost

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost`

The total cost for the previous day, including the standing charge.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `tariff_code` | `string` | The tariff that determined the cost |
| `standing_charge` | `float` | The standing charge included in the cost |
| `total_without_standing_charge` | `float` | The total cost of the previous day excluding the standing charge |
| `total` | `float` | The total cost for the previous day |
| `charges` | `array` | Collection of consumption periods and costs for the previous day broken down into 30 minute periods. |
| `last_calculated_timestamp` | `datetime` | The timestamp determining when the cost was last calculated. |

### Previous Accumulative Cost (Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_peak`

The total cost for the previous day that applied during peak hours. This is disabled by default. This will only be populated if you're on a tariff with two available rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

### Previous Accumulative Cost (Off Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_off_peak`

The total cost for the previous day that applied during off peak hours. This is disabled by default. This will only be populated if you're on a tariff with two available rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

## Export Sensors

If you export energy, then in addition you'll gain the above sensors with the name `export` present. E.g. `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_export_current_rate`.

## Home Mini Sensors

### Current Consumption

> This will only be available if you have specified you have a [Octopus Home Mini](../setup_account.md#home-mini). Do not set unless you have one

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_consumption`

The latest electricity consumption sent to Octopus Energy. This will update every minute. This is a legacy sensor which was been built to see the accumulation within the energy dashboard. This _may_ be removed in the future.

It has been noticed that daily consumption reported in Home Assistant can differ to when looking at past data within Octopus Energy. It looks like this is because Octopus Energy will favour "official" data from your smart meter over the data they collect.

If current consumption data is unable to be retrieved, then the integration will attempt to retrieve missing data. This will be done for the current day only. This is due to it sharing the same data for the accumulation sensors and will not be changed. 

| Attribute | Type | Description |
|-----------|------|-------------|
| `last_updated_timestamp` | `datetime` | The datetime the data was last retrieved |

### Current Demand

> This will only be available if you have specified you have a [Octopus Home Mini](../setup_account.md#home-mini). Do not set unless you have one

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_demand`

The current demand reported by the Home Mini. This will try and update every minute.

| Attribute | Type | Description |
|-----------|------|-------------|
| `last_updated_timestamp` | `datetime` | The datetime the data was last retrieved |

### Current Accumulative Consumption

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_consumption`

The total consumption reported by the meter for the current day.

| Attribute | Type | Description |
|-----------|------|-------------|

| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `total` | `float` | The total energy value for the previous day |
| `charges` | `array` | Collection of consumption periods for the previous day broken down into 30 minute periods. |

### Current Accumulative Consumptions (Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_consumption_peak`

The total consumption reported by the meter for the current day that applied during peak hours. This is disabled by default. This will only be populated if you're on a tariff with two available rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

### Current Accumulative Consumption (Off Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_consumption_off_peak`

The total consumption reported by the meter for the current day that applied during off peak hours. This is disabled by default. This will only be populated if you're on a tariff with two available rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

### Current Accumulative Cost

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_cost`

The total cost for the current day, including the standing charge.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `tariff_code` | `string` | The tariff that determined the cost |
| `standing_charge` | `float` | The standing charge included in the cost |
| `total_without_standing_charge` | `float` | The total cost of the current day excluding the standing charge |
| `total` | `float` | The total cost for the current day |
| `charges` | `array` | Collection of consumption periods and costs for the current day broken down into 30 minute periods. |

### Current Accumulative Cost (Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_cost_peak`

The total cost for the current day that applied during peak hours. This is disabled by default. This will only be populated if you're on a tariff with two available rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

### Current Accumulative Cost (Off Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_cost_off_peak`

The total cost for the current day that applied during off peak hours. This is disabled by default. This will only be populated if you're on a tariff with two available rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

## Tariff Overrides

You may be on an existing tariff but want to know if the grass is greener (or cheaper) on the other side. The following entities are available in a disabled state, which when enabled can give you an indication what you'd be paying if you were on a different tariff and didn't change your energy habits.

Instructions on how to find tariffs can be found in the [faq](../faq.md#i-want-to-use-the-tariff-overrides-but-how-do-i-find-an-available-tariff).

> Please note: When updating the tariff depending on what previous consumption data is available, it can take up to 24 hours to update the cost. This will be improved in the future.

### Previous Accumulative Cost Override Tariff (Electricity)

`text.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_override_tariff`

This is used to define the electricity tariff you want to compare

### Previous Accumulative Cost Override (Electricity)

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_override`

This is the cost of the previous electricity accumulation based on the specified tariff override.

For attributes, see [Previous Accumulative Cost](#previous-accumulative-cost).
