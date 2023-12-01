# Electricity Entities

You'll get the following entities for each electricity meter with an active agreement.

- [Electricity Entities](#electricity-entities)
  - [Current Rate](#current-rate)
  - [Previous Rate](#previous-rate)
  - [Next rate](#next-rate)
  - [Current Day Rates](#current-day-rates)
  - [Previous Day Rates](#previous-day-rates)
  - [Next Day Rates](#next-day-rates)
  - [Off Peak](#off-peak)
  - [Smart Meter Entities](#smart-meter-entities)
    - [Previous Accumulative Consumption](#previous-accumulative-consumption)
    - [Previous Accumulative Consumptions (Peak Rate)](#previous-accumulative-consumptions-peak-rate)
    - [Previous Accumulative Consumption (Off Peak Rate)](#previous-accumulative-consumption-off-peak-rate)
    - [Previous Accumulative Cost](#previous-accumulative-cost)
    - [Previous Accumulative Cost (Peak Rate)](#previous-accumulative-cost-peak-rate)
    - [Previous Accumulative Cost (Off Peak Rate)](#previous-accumulative-cost-off-peak-rate)
  - [Previous Consumption Day Rates](#previous-consumption-day-rates)
  - [Export Entities](#export-entities)
  - [Home Mini Entities](#home-mini-entities)
    - [Current Consumption](#current-consumption)
    - [Current Demand](#current-demand)
    - [Current Accumulative Consumption](#current-accumulative-consumption)
    - [Current Accumulative Consumptions (Peak Rate)](#current-accumulative-consumptions-peak-rate)
    - [Current Accumulative Consumption (Off Peak Rate)](#current-accumulative-consumption-off-peak-rate)
    - [Current Accumulative Cost](#current-accumulative-cost)
    - [Current Accumulative Cost (Peak Rate)](#current-accumulative-cost-peak-rate)
    - [Current Accumulative Cost (Off Peak Rate)](#current-accumulative-cost-off-peak-rate)
  - [Tariff Overrides](#tariff-overrides)
    - [Previous Accumulative Cost Override Tariff](#previous-accumulative-cost-override-tariff)
      - [How To Use](#how-to-use)
    - [Previous Accumulative Cost Override](#previous-accumulative-cost-override)
    - [Previous Consumption Override Day Rates](#previous-consumption-override-day-rates)

## Current Rate

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_rate`

The current rate that energy consumption is charged at (including VAT).

This is in pounds and pence (e.g. 1.01 = £1.01).

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `tariff` | `string` | The tariff the meter/rates are associated with |
| `start` | `datetime` | The date/time when the rate started |
| `end` | `datetime` | The date/time when the rate ends |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup_account.md#pricing-caps) |
| `is_intelligent_adjusted` | `boolean` | Indicates if the rate has been adjusted due to a dispatch organised by an intelligent tariff |
| `current_day_min_rate` | `float` | The minimum rate available for the current day |
| `current_day_max_rate` | `float` | The maximum rate available for the current day |
| `current_day_average_rate` | `float` | The average rate for the current day |
| `price_cap` | `float` | The price cap that has been configured for the account and is currently applied to all electricity rates |

## Previous Rate

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_rate`

The previous rate that energy consumption was charged at (including VAT), that differs from the current rate. If there is no previous rate (e.g. rates before now are of the same value as the current rate), then this will be reported as `unknown`/`none`.

This is in pounds and pence (e.g. 1.01 = £1.01).

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `start` | `datetime` | The date/time when the previous rate started |
| `end` | `datetime` | The date/time when the previous rate ended |

## Next rate

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_next_rate`

The next/upcoming rate that energy consumption will be charged at (including VAT), that differs from the current rate. If there is no next rate (e.g. rates after now are of the same value as the current rate), then this will be reported as `unknown`/`none`.

This is in pounds and pence (e.g. 1.01 = £1.01).

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `start` | `datetime` | The date/time when the next rate starts |
| `end` | `datetime` | The date/time when the next rate ends |

## Current Day Rates

`event.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_day_rates`

The state of this sensor states when the current day's rates were last updated. The attributes of this sensor exposes the current day's rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the current day |
| `tariff_code` | `string` | The tariff code associated with current day's rates |
| `serial_number` | `string` | The serial number of the meter the rates are related to |
| `mpan` | `string` | The MPAN of the meter the rates are related to |

Each rate item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the rate starts |
| `end` | `datetime` | The date/time when the rate ends |
| `value_inc_vat` | `float` | The value of the rate including VAT. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup_account.md#pricing-caps) |
| `is_intelligent_adjusted` | `boolean` | Indicates if the rate has been adjusted due to a dispatch organised by an intelligent tariff |

## Previous Day Rates

`event.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_day_rates`

The state of this sensor states when the previous day's rates were last updated. The attributes of this sensor exposes the previous day's rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the previous day |
| `tariff_code` | `string` | The tariff code associated with previous day's rates |
| `serial_number` | `string` | The serial number of the meter the rates are related to |
| `mpan` | `string` | The MPAN of the meter the rates are related to |

Each rate item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the rate starts |
| `end` | `datetime` | The date/time when the rate ends |
| `value_inc_vat` | `float` | The value of the rate including VAT. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup_account.md#pricing-caps) |
| `is_intelligent_adjusted` | `boolean` | Indicates if the rate has been adjusted due to a dispatch organised by an intelligent tariff |

## Next Day Rates

`event.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_next_day_rates`

The state of this sensor states when the next day's rates were last updated. The attributes of this sensor exposes the next day's rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the next day |
| `tariff_code` | `string` | The tariff code associated with today's rates |
| `serial_number` | `string` | The serial number of the meter the rates are related to |
| `mpan` | `string` | The MPAN of the meter the rates are related to |

Each rate item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the rate starts |
| `end` | `datetime` | The date/time when the rate ends |
| `value_inc_vat` | `float` | The value of the rate including VAT. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup_account.md#pricing-caps) |
| `is_intelligent_adjusted` | `boolean` | Indicates if the rate has been adjusted due to a dispatch organised by an intelligent tariff |

## Off Peak

`binary_sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_off_peak`

This is `on` when you're within your tariff's off peak period, and `off` at all other times. This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). This will only be work if you're on a tariff with an off peak period.

## Smart Meter Entities

If your account information doesn't determine you have a smart meter, then you will have the following entities in a disabled state. If you enable these entities, they might not work correctly in this scenario.

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
| `total` | `float` | The total energy value for the previous day. |
| `charges` | `array` | Collection of consumption periods for the previous day broken down into 30 minute periods. |
| `last_evaluated` | `datetime` | The date/time that the consumption sensor was last evaluated. |

Each charge item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the consumption starts |
| `end` | `datetime` | The date/time when the consumption ends |
| `consumption` | `float` | The consumption value of the specified period |

### Previous Accumulative Consumptions (Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption_peak`

The total consumption reported by the meter for the previous day that applied during peak hours. This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). This will only be populated if you're on a tariff with two available rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

### Previous Accumulative Consumption (Off Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption_off_peak`

The total consumption reported by the meter for the previous day that applied during off peak hours. This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). This will only be populated if you're on a tariff with two available rates.

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
| `standing_charge` | `float` | The standing charge included in the cost. This is in pounds and pence (e.g. 1.01 = £1.01)  |
| `total_without_standing_charge` | `float` | The total cost of the previous day excluding the standing charge. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `total` | `float` | The total cost for the previous day. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `charges` | `array` | Collection of consumption periods and costs for the previous day broken down into 30 minute periods. |
| `last_evaluated` | `datetime` | The timestamp determining when the cost was last evaluated. |

Each charge item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the consumption starts |
| `end` | `datetime` | The date/time when the consumption ends |
| `rate` | `float` | The rate the consumption is charged at. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `consumption` | `float` | The consumption value of the specified period |
| `cost` | `float` | The cost of the consumption at the specified rate. This is in pounds and pence (e.g. 1.01 = £1.01) |

### Previous Accumulative Cost (Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_peak`

The total cost for the previous day that applied during peak hours. This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). This will only be populated if you're on a tariff with two available rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

### Previous Accumulative Cost (Off Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_off_peak`

The total cost for the previous day that applied during off peak hours. This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). This will only be populated if you're on a tariff with two available rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

## Previous Consumption Day Rates

`event.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_consumption_rates`

The state of this sensor states when the previous consumption's rates were last updated. This is typically the same as the previous day's rates, but could differ if the default offset is changed. The attributes of this sensor exposes the previous consumption's rates. This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the previous consumption |
| `tariff_code` | `string` | The tariff code associated with previous consumption's rates |

Each rate item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the rate starts |
| `end` | `datetime` | The date/time when the rate ends |
| `value_inc_vat` | `float` | The value of the rate including VAT. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup_account.md#pricing-caps) |
| `is_intelligent_adjusted` | `boolean` | Indicates if the rate has been adjusted due to a dispatch organised by an intelligent tariff |

## Export Entities

If you export energy, then in addition you'll gain the above entities with the name `export` present. E.g. `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_export_current_rate`.

## Home Mini Entities

### Current Consumption

> This will only be available if you have specified you have a [Octopus Home Mini](../setup_account.md#home-mini). Do not set unless you have one

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_consumption`

The latest electricity consumption sent to Octopus Energy. This will update every minute. This is a legacy sensor which was been built to see the accumulation within the energy dashboard. This _may_ be removed in the future.

It has been noticed that daily consumption reported in Home Assistant can differ to when looking at past data within Octopus Energy. It looks like this is because Octopus Energy will favour "official" data from your smart meter over the data they collect.

If current consumption data is unable to be retrieved, then the integration will attempt to retrieve missing data. This will be done for the current day only. This is due to it sharing the same data for the accumulation sensors and will not be changed. 

| Attribute | Type | Description |
|-----------|------|-------------|
| `last_evaluated` | `datetime` | The datetime the data was last evaluated |

### Current Demand

> This will only be available if you have specified you have a [Octopus Home Mini](../setup_account.md#home-mini). Do not set unless you have one

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_demand`

The current demand reported by the Home Mini. This will try and update every minute.

| Attribute | Type | Description |
|-----------|------|-------------|
| `last_evaluated` | `datetime` | The datetime the data was last evaluated |

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

Each charge item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the consumption starts |
| `end` | `datetime` | The date/time when the consumption ends |
| `consumption` | `float` | The consumption value of the specified period |

### Current Accumulative Consumptions (Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_consumption_peak`

The total consumption reported by the meter for the current day that applied during peak hours. This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). This will only be populated if you're on a tariff with two available rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

### Current Accumulative Consumption (Off Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_consumption_off_peak`

The total consumption reported by the meter for the current day that applied during off peak hours. This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). This will only be populated if you're on a tariff with two available rates.

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
| `standing_charge` | `float` | The standing charge included in the cost. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `total_without_standing_charge` | `float` | The total cost of the current day excluding the standing charge. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `total` | `float` | The total cost for the current day. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `charges` | `array` | Collection of consumption periods and costs for the current day broken down into 30 minute periods. |

Each charge item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the consumption starts |
| `end` | `datetime` | The date/time when the consumption ends |
| `rate` | `float` | The rate the consumption is charged at. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `consumption` | `float` | The consumption value of the specified period |
| `cost` | `float` | The cost of the consumption at the specified rate. This is in pounds and pence (e.g. 1.01 = £1.01) |

### Current Accumulative Cost (Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_cost_peak`

The total cost for the current day that applied during peak hours. This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). This will only be populated if you're on a tariff with two available rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

### Current Accumulative Cost (Off Peak Rate) 

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_cost_off_peak`

The total cost for the current day that applied during off peak hours. This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). This will only be populated if you're on a tariff with two available rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

## Tariff Overrides

You may be on an existing tariff but want to know if the grass is greener (or cheaper) on the other side. The following entities are available in a disabled state, which when enabled can give you an indication what you'd be paying if you were on a different tariff and didn't change your energy habits.

See [below](#previous-accumulative-cost-override-tariff-electricity) for instructions on how to set up.

> Please note: When updating the tariff depending on what previous consumption data is available, it can take up to 24 hours to update the cost. This will be improved in the future.

### Previous Accumulative Cost Override Tariff

`text.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_override_tariff`

This is used to define the electricity tariff you want to compare.

#### How To Use

Instructions on how to find tariffs can be found in the [faq](../faq.md#i-want-to-use-the-tariff-overrides-but-how-do-i-find-an-available-tariff).

Once you have found your target tariff

1. Click on this entity to open the info dialog.
2. Enter your tariff in the text box, and hit `enter` on your keyboard to confirm

> Please note: When updating the tariff depending on what previous consumption data is available, it can take up to 24 hours to update the cost. This will be improved in the future.

### Previous Accumulative Cost Override

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_override`

This is the cost of the previous electricity accumulation based on the specified tariff override.

For attributes, see [Previous Accumulative Cost](#previous-accumulative-cost).

### Previous Consumption Override Day Rates

`event.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_consumption_override_rates`

The state of this sensor states when the previous consumption override's rates were last updated. The attributes of this sensor exposes the previous consumption override's rates. This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). 

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `list` | The list of rates applicable for the previous consumption override |
| `tariff_code` | `string` | The tariff code associated with previous consumption override's rates |

Each rate item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the rate starts |
| `end` | `datetime` | The date/time when the rate ends |
| `value_inc_vat` | `float` | The value of the rate including VAT. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup_account.md#pricing-caps) |
| `is_intelligent_adjusted` | `boolean` | Indicates if the rate has been adjusted due to a dispatch organised by an intelligent tariff |