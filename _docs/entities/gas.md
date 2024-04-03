# Gas

You'll get the following entities for each gas meter with an active agreement:

## Current Rate

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_rate`

The current rate that energy consumption is charged at (including VAT).

| Attribute | Type | Description |
|-----------|------|-------------|
| `mprn` | `string` | The mprn for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `tariff` | `string` | The tariff the meter/rates are associated with |
| `start` | `datetime` | The date/time when the rate started |
| `end` | `datetime` | The date/time when the rate ends |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup/account.md#pricing-caps) |
| `price_cap` | `float` | The price cap that has been configured for the account and is currently applied to all gas rates |

## Previous Rate

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_rate`

The previous rate that energy consumption was charged at (including VAT), that differs from the current rate. If there is no previous rate (e.g. rates before now are of the same value as the current rate), then this will be reported as `unknown`/`none`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mprn` | `string` | The mprn for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `start` | `datetime` | The date/time when the rate started |
| `end` | `datetime` | The date/time when the rate ended |

## Next rate

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_next_rate`

The next/upcoming rate that energy consumption will be charged at (including VAT), that differs from the current rate. If there is no next rate (e.g. rates after now are of the same value as the current rate), then this will be reported as `unknown`/`none`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mprn` | `string` | The mprn for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `start` | `datetime` | The date/time when the rate starts |
| `end` | `datetime` | The date/time when the rate ends |

## Current Day Rates

`event.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_day_rates`

The state of this sensor states when the current day's rates were last updated. The attributes of this sensor exposes the current day's rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the current day |
| `tariff_code` | `string` | The tariff code associated with current day's rates |

Each rate item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the rate starts |
| `end` | `datetime` | The date/time when the rate ends |
| `value_inc_vat` | `float` | The value of the rate including VAT. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup/account.md#pricing-caps) |

## Previous Day Rates

`event.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_day_rates`

The state of this sensor states when the previous day's rates were last updated. The attributes of this sensor exposes the previous day's rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the previous day |
| `tariff_code` | `string` | The tariff code associated with previous day's rates |

Each rate item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the rate starts |
| `end` | `datetime` | The date/time when the rate ends |
| `value_inc_vat` | `float` | The value of the rate including VAT. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup/account.md#pricing-caps) |

## Next Day Rates

`event.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_next_day_rates`

The state of this sensor states when the next day's rates were last updated. The attributes of this sensor exposes the next day's rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the next day |
| `tariff_code` | `string` | The tariff code associated with today's rates |

Each rate item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the rate starts |
| `end` | `datetime` | The date/time when the rate ends |
| `value_inc_vat` | `float` | The value of the rate including VAT. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup/account.md#pricing-caps) |

## Smart Meter Entities

If your account information doesn't determine you have a smart meter, then you will have the following entities in a disabled state. If you enable these entities, they might not work correctly in this scenario. 

If you are wishing to use these sensors with the Energy Dashboard, then you can follow this [guide](../setup/energy_dashboard.md).

> By default, it's not possible to include current consumption sensors. This is due to Octopus Energy only receive data from the smart meters up to the previous day.

### Previous Accumulative Consumption (m3)

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption_m3`

The total consumption reported by the meter for the previous day in m3. If your meter reports in m3, then this will be an accurate value reported by Octopus, otherwise it will be a calculated/estimated value.

!!! info

    This data won't necessarily be available at the stroke of midnight and has been reported to take up to 18 hours for it to appear. This integration has no control of this and is at the mercy of when the data is available by Octopus Energy. If data is not available within the 24 hour timeframe, then the integration will not be able to pick up and display the data.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mprn` | `string` | The mprn for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_estimated` | `boolean` | Determines if the consumption was estimated. This can occur if your meter reports in `kwh`. |
| `total_kwh` | `float` | The total energy value for the previous day in `kwh`. If your meter reports in `m3`, then this will be estimated using your set [calorific value](../setup/account.md#calorific-value) |
| `total_m3` | `float` | The total energy value for the previous day in `m3`. If your meter reports in `kwh`, then this will be estimated using your set [calorific value](../setup/account.md#calorific-value) |
| `last_evaluated` | `datetime` | The timestamp determining when the consumption was last calculated. |
| `charges` | `array` | Collection of consumption periods for the previous day broken down into 30 minute periods. |
| `calorific_value` | `float` | The calorific value used for the calculations, as set in your [account](../setup/account.md#calorific-value). |
| `data_last_retrieved` | `datetime` | The timestamp when the underlying data was last refreshed from the OE servers |
| `latest_available_data_timestamp` | `datetime` | The date/time of the latest available consumption data via the API. This is only for data reported directly by the meter and won't include data reported by other devices (e.g. Octopus Home Mini) |

Each charge item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the consumption starts |
| `end` | `datetime` | The date/time when the consumption ends |
| `consumption` | `float` | The consumption value of the specified period |

### Previous Accumulative Consumption (kWh)

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption_kwh`

The total consumption reported by the meter for the previous day in kwh. If your meter reports in kwh, then this will be an accurate value reported by Octopus, otherwise it will be a calculated/estimated value.

!!! info

    This data won't necessarily be available at the stroke of midnight and has been reported to take up to 18 hours for it to appear. This integration has no control of this and is at the mercy of when the data is available by Octopus Energy. If data is not available within the 24 hour timeframe, then the integration will not be able to pick up and display the data.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mprn` | `string` | The mprn for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_estimated` | `boolean` | Determines if the consumption was estimated. This can occur if your meter reports in `m3`. |
| `last_evaluated` | `datetime` | The timestamp determining when the consumption was last calculated. |
| `charges` | `array` | Collection of consumption periods for the previous day broken down into 30 minute periods. |
| `calorific_value` | `float` | The calorific value used for the calculations, as set in your [account](../setup/account.md#calorific-value). |
| `data_last_retrieved` | `datetime` | The timestamp when the underlying data was last refreshed from the OE servers |
| `latest_available_data_timestamp` | `datetime` | The date/time of the latest available consumption data via the API. This is only for data reported directly by the meter and won't include data reported by other devices (e.g. Octopus Home Mini) |

Each charge item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the consumption starts |
| `end` | `datetime` | The date/time when the consumption ends |
| `consumption` | `float` | The consumption value of the specified period |

### Previous Accumulative Cost

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_cost`

The total cost for the previous day, including the standing charge.

!!! info

    This will only populate once the consumption data is available.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mprn` | `string` | The mprn for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `tariff_code` | `string` | The tariff that determined the cost |
| `standing_charge` | `float` | The standing charge included in the cost. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `total_without_standing_charge` | `float` | The total cost of the previous day excluding the standing charge. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `total` | `float` | The total cost for the previous day. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `charges` | `array` | Collection of consumption periods and costs for the previous day broken down into 30 minute periods. |
| `last_evaluated` | `datetime` | The timestamp determining when the cost was last calculated. |
| `calorific_value` | `float` | The calorific value used for the calculations, as set in your [account](../setup/account.md#calorific-value). |

Each charge item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the consumption starts |
| `end` | `datetime` | The date/time when the consumption ends |
| `rate` | `float` | The rate the consumption is charged at. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `consumption` | `float` | The consumption value of the specified period |
| `cost` | `float` | The cost of the consumption at the specified rate. This is in pounds and pence (e.g. 1.01 = £1.01) |

## Previous Consumption Day Rates

`event.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_consumption_rates`

The state of this sensor states when the previous consumption's rates were last updated. This is typically the same as the previous day's rates, but could differ if the default offset is changed. The attributes of this sensor exposes the previous consumption's rates. 

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the previous consumption |
| `tariff_code` | `string` | The tariff code associated with previous consumption's rates |

Each rate item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the rate starts |
| `end` | `datetime` | The date/time when the rate ends |
| `value_inc_vat` | `float` | The value of the rate including VAT. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup/account.md#pricing-caps) |

## Home Mini Entities

### Current Consumption

> This will only be available if you have specified you have a [Octopus Home Mini](../setup/account.md#home-mini). Do not set unless you have one

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_consumption`

The latest gas consumption sent to Octopus Energy. By default, this will update every minute. This has been built to see the accumulation within the energy dashboard. If you are wanting a sensor to see the current day's accumulation, then you will need to use something like [utility meter](https://www.home-assistant.io/integrations/utility_meter/). It has been noticed that daily consumption reported in Home Assistant can differ to when looking at past data within Octopus Energy. It looks like this is because Octopus Energy will favour "official" data from your smart meter over the data they collect.

If current consumption data is unable to be retrieved, then the integration will attempt to retrieve missing data. This will be done up to 5 days behind to give a buffer before the API requires a higher interval and will not be changed.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mprn` | `string` | The mprn for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |

### Current Accumulative Consumption (m3)

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_accumulative_consumption_m3`

The total consumption reported by the meter for the current day in m3. This is calculated/estimated using your set [calorific value](../setup/account.md#calorific-value) from the kWh data reported by Octopus Energy.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mprn` | `string` | The mprn for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `last_evaluated` | `datetime` | The timestamp determining when the consumption was last calculated. |
| `charges` | `array` | Collection of consumption periods for the current day broken down into 30 minute periods. |
| `calorific_value` | `float` | The calorific value used for the calculations, as set in your [account](../setup/account.md#calorific-value). |
| `data_last_retrieved` | `datetime` | The timestamp when the underlying data was last refreshed from the OE servers |

Each charge item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the consumption starts |
| `end` | `datetime` | The date/time when the consumption ends |
| `consumption` | `float` | The consumption value of the specified period |

### Current Accumulative Consumption (kWh)

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_accumulative_consumption_kwh`

The total consumption reported by the meter for the current day in kWh. This is natively reported by Octopus Energy.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mprn` | `string` | The mprn for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `last_evaluated` | `datetime` | The timestamp determining when the consumption was last calculated. |
| `charges` | `array` | Collection of consumption periods for the current day broken down into 30 minute periods. |
| `calorific_value` | `float` | The calorific value used for the calculations, as set in your [account](../setup/account.md#calorific-value). |
| `data_last_retrieved` | `datetime` | The timestamp when the underlying data was last refreshed from the OE servers |

Each charge item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the consumption starts |
| `end` | `datetime` | The date/time when the consumption ends |
| `consumption` | `float` | The consumption value of the specified period |

### Current Accumulative Cost

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_accumulative_cost`

The total cost for the current day, including the standing charge.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mprn` | `string` | The mprn for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
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

## Tariff Overrides

You may be on an existing tariff but want to know if the grass is greener (or cheaper) on the other side. The following entities are available in a disabled state, which when enabled can give you an indication what you'd be paying if you were on a different tariff and didn't change your energy habits.

Instructions on how to find tariffs can be found in the [faq](../faq.md#i-want-to-use-the-tariff-overrides-but-how-do-i-find-an-available-tariff).

!!! info
  
    When updating the tariff depending on what previous consumption data is available, it can take up to 24 hours to update the cost. This will be improved in the future.

### Previous Accumulative Cost Override Tariff

`text.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_cost_override_tariff`

This is used to define the gas tariff you want to compare

#### How To Use

Instructions on how to find tariffs can be found in the [faq](../faq.md#i-want-to-use-the-tariff-overrides-but-how-do-i-find-an-available-tariff).

Once you have found your target tariff

1. Click on this entity to open the info dialog.
2. Enter your tariff in the text box, and hit `enter` on your keyboard to confirm

!!! info

    When updating the tariff depending on what previous consumption data is available, it can take up to 24 hours to update the cost. This will be improved in the future.

### Previous Accumulative Cost Override

`sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_cost_override`

This is the cost of the previous gas accumulation based on the specified tariff override.

For attributes, see [Previous Accumulative Cost](#previous-accumulative-cost).

### Previous Consumption Override Day Rates

`event.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_consumption_override_rates`

The state of this sensor states when the previous consumption override's rates were last updated. The attributes of this sensor exposes the previous consumption override's rates. 

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the previous consumption override |
| `tariff_code` | `string` | The tariff code associated with previous consumption override's rates |

Each rate item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the rate starts |
| `end` | `datetime` | The date/time when the rate ends |
| `value_inc_vat` | `float` | The value of the rate including VAT. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup/account.md#pricing-caps) |
