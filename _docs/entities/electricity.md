# Electricity

You'll get the following entities for each electricity meter with an active agreement.

## Current Rate

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_rate`

The current rate that energy consumption is charged at (including VAT).

This is in pounds and pence (e.g. 1.01 = £1.01).

!!! warning

    If you are on an intelligent tariff, then rate information will be adjusted to off-peak rates when a dispatch is discovered during the period. This off peak rate will be dependent on your car charging. As the integration has no knowledge of if your car is charging, this value might be incorrect. This is indicated via the `is_intelligent_adjusted` attribute.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `tariff` | `string` | The tariff the meter/rates are associated with |
| `start` | `datetime` | The date/time when the rate started |
| `end` | `datetime` | The date/time when the rate ends |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup/account.md#pricing-caps) |
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
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup/account.md#pricing-caps) |
| `is_intelligent_adjusted` | `boolean` | Indicates if the rate has been adjusted due to a dispatch organised by an intelligent tariff |

## Next rate

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_next_rate`

The next/upcoming rate that energy consumption will be charged at (including VAT), that differs from the current rate. If there is no next rate (e.g. rates after now are of the same value as the current rate), then this will be reported as `unknown`/`none`.

This is in pounds and pence (e.g. 1.01 = £1.01).

!!! warning

    If you are on an intelligent tariff, then rate information will be adjusted to off-peak rates when a dispatch is discovered during the period. This off peak rate will be dependent on your car charging. As the integration has no knowledge of if your car is charging, this value might be incorrect. This is indicated via the `is_intelligent_adjusted` attribute.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `start` | `datetime` | The date/time when the next rate starts |
| `end` | `datetime` | The date/time when the next rate ends |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup/account.md#pricing-caps) |
| `is_intelligent_adjusted` | `boolean` | Indicates if the rate has been adjusted due to a dispatch organised by an intelligent tariff |

## Current Day Rates

`event.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_day_rates`

The state of this sensor states when the current day's rates were last updated. The attributes of this sensor exposes the current day's rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the current day |
| `tariff_code` | `string` | The tariff code associated with current day's rates |
| `serial_number` | `string` | The serial number of the meter the rates are related to |
| `mpan` | `string` | The MPAN of the meter the rates are related to |

Each rate item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the rate starts |
| `end` | `datetime` | The date/time when the rate ends |
| `value_inc_vat` | `float` | The value of the rate including VAT. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup/account.md#pricing-caps) |
| `is_intelligent_adjusted` | `boolean` | Indicates if the rate has been adjusted due to a dispatch organised by an intelligent tariff |

## Previous Day Rates

`event.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_day_rates`

The state of this sensor states when the previous day's rates were last updated. The attributes of this sensor exposes the previous day's rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the previous day |
| `tariff_code` | `string` | The tariff code associated with previous day's rates |
| `serial_number` | `string` | The serial number of the meter the rates are related to |
| `mpan` | `string` | The MPAN of the meter the rates are related to |

Each rate item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the rate starts |
| `end` | `datetime` | The date/time when the rate ends |
| `value_inc_vat` | `float` | The value of the rate including VAT. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup/account.md#pricing-caps) |
| `is_intelligent_adjusted` | `boolean` | Indicates if the rate has been adjusted due to a dispatch organised by an intelligent tariff |

## Next Day Rates

`event.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_next_day_rates`

The state of this sensor states when the next day's rates were last updated. The attributes of this sensor exposes the next day's rates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `rates` | `array` | The list of rates applicable for the next day |
| `tariff_code` | `string` | The tariff code associated with today's rates |
| `serial_number` | `string` | The serial number of the meter the rates are related to |
| `mpan` | `string` | The MPAN of the meter the rates are related to |

Each rate item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the rate starts |
| `end` | `datetime` | The date/time when the rate ends |
| `value_inc_vat` | `float` | The value of the rate including VAT. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `is_capped` | `boolean` | Indicates if the rate has been capped by a [configured price cap](../setup/account.md#pricing-caps) |
| `is_intelligent_adjusted` | `boolean` | Indicates if the rate has been adjusted due to a dispatch organised by an intelligent tariff |

## Off Peak

`binary_sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_off_peak`

This is `on` when you're within your tariff's off peak period, and `off` at all other times. This will only be work if you're on a tariff with an off peak period.

!!! warning

    For intelligent tariffs, this sensor will turn on when you're within active ad hoc dispatching periods as well.

    Depending on your [account configuration](../setup/account.md#intelligent-rates-mode), what is determined as an active dispatching period will change. If you have configured to accept [planned or started dispatches](../setup/account.md#planned-and-started-dispatches-will-turn-into-off-peak-rates), then the sensor will turn on when you're are within an active planned or started dispatch period. If you have configured to accept [only started dispatches](../setup/account.md#only-started-dispatches-will-turn-into-off-peak-rates), then the sensor will turn on when you're are within an active started dispatch period, but not planned dispatch.

    This above does not apply and will not come on outside of the standard off peak hours for the following intelligent providers

    * OHME

!!! note

    Sensor came on when you did/didn't expected it to and you're on an intelligent tariff? You can see what the state of your dispatches were at the time by using the [get_point_in_time_intelligent_dispatch_history service](../services.md#octopus_energyget_point_in_time_intelligent_dispatch_history)

| Attribute | Type | Description |
|-----------|------|-------------|
| `current_start` | `datetime` | The date/time when the off peak rate started |
| `current_end` | `datetime` | The date/time when the off peak rate ends |
| `next_start` | `datetime` | The date/time when the next off peak rate starts |
| `next_end` | `datetime` | The date/time when the next off peak rate ends |

## Smart Meter Entities

If your account information doesn't determine you have a smart meter, then you will have the following entities in a disabled state. If you enable these entities, they might not work correctly in this scenario.

If you are wishing to use these sensors with the Energy Dashboard, then you can follow this [guide](../setup/energy_dashboard.md).

> By default, it's not possible to include current consumption sensors. This is due to Octopus Energy only receive data from the smart meters up to the previous day. If you want current consumption, then you will need a [Octopus Home Mini](https://octopus.energy/blog/octopus-home-mini/).

### Previous Accumulative Consumption

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption`

The total consumption reported by the meter (not other devices e.g. Home Mini) for the previous available full day. If for example data is available up to `01:00` of `2024-09-02`, then this sensor will report the cost between `2024-09-01T00:00:00Z` and `2024-09-02T00:00:00Z`.

Due to limitation of HA entities, the data will be updated as a single record, which means the history of the sensor will not be broken down further than once a day. If you want the cost broken down into hourly chunks, you can use the statistic entities used for the [energy dashboard](../setup/energy_dashboard.md#previous-day-consumption).

!!! info

    This retrieves the data reported directly by the meter which is used to calculate your bill. If you have an Octopus Home Mini (or similar), then data reported by this device will not be exposed in this sensor. This is to avoid confusion when comparing the data against your bill and to provide consistency between users with and without an Octopus Home Mini.

!!! warning

    This data won't necessarily be available at the stroke of midnight. This integration has no control of this and is at the mercy of when the data is available by Octopus Energy. 
    
    Because this sensor only looks at the last complete day, if the data takes longer than 24 hours to populate then the sensor will not update straight away. You can look at the [data_last_retrieved sensor](./diagnostics.md#previous-consumption-and-rates-data-last-retrieved) which indicates when the data was last retrieved.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |
| `total` | `float` | The total energy value for the previous day. |
| `charges` | `array` | Collection of consumption periods for the previous day broken down into 30 minute periods. |

Each charge item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the consumption starts |
| `end` | `datetime` | The date/time when the consumption ends |
| `consumption` | `float` | The consumption value of the specified period |

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#previous-consumption-and-rates-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

#### Variants

The following variants of the [Previous Accumulative Consumption](#previous-accumulative-consumption) are available.

##### Off Peak

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption_off_peak`

The total consumption reported by the meter for the previous available full day during off peak hours (the lowest available rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

!!! warning

    If you are on intelligent and are using a provider where [planned_dispatches](./intelligent.md#is-dispatching) are not supported, then charges outside of your normal off peak periods will be counted at peak. This is because Octopus Energy doesn't provide enough information to determine if a completed dispatch was a bump charge or a planned charge.

##### Standard

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption_standard`

The total consumption reported by the meter for the previous available full day during standard hours (the middle rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

##### Peak

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption_peak`

The total consumption reported by the meter for the previous available full day during peak hours (the highest available rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

### Previous Accumulative Cost

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost`

The total cost for the previous available full day, including the standing charge. If for example data is available up to `01:00` of `2024-09-02`, then this sensor will report the cost between `2024-09-01T00:00:00Z` and `2024-09-02T00:00:00Z`. 

Due to limitation of HA entities, the data will be updated as a single record, which means the history of the sensor will not be broken down further than once a day. If you want the cost broken down into hourly chunks, you can use the statistic entities used for the [energy dashboard](../setup/energy_dashboard.md#previous-day-consumption).

!!! info

    This retrieves the data reported directly by the meter which is used to calculate your bill. If you have an Octopus Home Mini (or similar), then data reported by this device will not be exposed in this sensor. This is to avoid confusion when comparing the data against your bill and to provide consistency between users with and without an Octopus Home Mini.

!!! info
    If you are on an intelligent tariff, this will not include charges that are done outside of normal off peak hours in certain scenarios. See the [FAQ](../faq.md#im-on-an-intelligent-tariff-but-the-cost-sensors-are-out-is-this-normal) for more information around this.

!!! warning

    This data won't necessarily be available at the stroke of midnight. This integration has no control of this and is at the mercy of when the data is available by Octopus Energy. 
    
    Because this sensor only looks at the last complete day, if the data takes longer than 24 hours to populate then the sensor will not update straight away. You can look at the [data_last_retrieved sensor](./diagnostics.md#previous-consumption-and-rates-data-last-retrieved) which indicates when the data was last retrieved.

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

Each charge item has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the consumption starts |
| `end` | `datetime` | The date/time when the consumption ends |
| `rate` | `float` | The rate the consumption is charged at. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `consumption` | `float` | The consumption value of the specified period |
| `cost` | `float` | The cost of the consumption at the specified rate. This is in pounds and pence (e.g. 1.01 = £1.01) |

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#previous-consumption-and-rates-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

#### Variants

The following variants of the [Previous Accumulative Cost](#previous-accumulative-cost) are available.

##### Off Peak

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_off_peak`

The total cost reported by the meter for the previous available full day during off peak hours (the lowest available rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

!!! warning

    If you are on intelligent and are using a provider where [planned_dispatches](./intelligent.md#is-dispatching) are not supported, then charges outside of your normal off peak periods will be counted at peak. This is because Octopus Energy doesn't provide enough information to determine if a completed dispatch was a bump charge or a planned charge.

##### Standard

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_standard`

The total cost reported by the meter for the previous available full day during standard hours (the middle rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

##### Peak

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_peak`

The total cost reported by the meter for the previous available full day during peak hours (the highest available rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

## Previous Consumption Day Rates

`event.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_consumption_rates`

The state of this sensor states when the previous consumption's rates were last updated. This is typically the same as the previous available full day's rates, but could differ depending on available data. The attributes of this sensor exposes the previous consumption's rates. 

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
| `is_intelligent_adjusted` | `boolean` | Indicates if the rate has been adjusted due to a dispatch organised by an intelligent tariff |

## Export Entities

If you export energy, then unless specified otherwise, in addition you'll gain the above entities with the name `export` present. E.g. `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_export_current_rate`.

## Home Mini/Pro Entities

### Current Consumption

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_consumption`

!!! warning
    This will only be available if you have specified you have an [Octopus Home Mini](../setup/account.md#home-mini). Do not set unless you have one.

!!! info
    An export equivalent of this sensor does not exist because the data is not available

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

The delta of the accumulative electricity consumption since the last update (e.g. if the previous accumulative consumption update reported 1kWh and the current accumulative consumption update reported 1.1kWh, then this sensor will report 0.1kWh). The time period the data for this sensor represents will depend on the frequency the underlying data is retrieved. If the data takes longer to refresh, then the time period of this sensor will be extended.

This is a legacy sensor which was been built to see the accumulation within the energy dashboard. This _may_ be removed in the future.

It has been noticed that daily consumption reported in Home Assistant can differ to when looking at past data within Octopus Energy. It looks like this is because Octopus Energy will favour "official" data from your smart meter over the data they collect.

If current consumption data is unable to be retrieved, then the integration will attempt to retrieve missing data. This will be done for the current day only. This is due to it sharing the same data for the accumulation sensors and will not be changed. 

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#current-consumption-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

### Current Demand

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_demand`

!!! warning
    This will only be available if you have specified you have an [Octopus Home Mini](../setup/account.md#home-mini) or have configured an [Octopus Home Pro](../setup//account.md#home-pro). Do not set unless you have one.

The current demand reported by the Home Mini/Pro. This will try and update every minute for Home Mini and every 10 seconds for Home Pro.

!!! info

    You can use the [Home Mini data_last_retrieved sensor](./diagnostics.md#current-consumption-data-last-retrieved) or [Home Pro data_last_retrieved sensor](./diagnostics.md#current-consumption-home-pro-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.

### Current Accumulative Consumption

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_consumption`

!!! warning
    This will only be available if you have specified you have an [Octopus Home Mini](../setup/account.md#home-mini). Do not set unless you have one.

!!! info
    An export equivalent of this sensor does not exist because the data is not available

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

### Current Total Consumption

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_total_consumption`

!!! warning
    This will only be available if you have specified you have an [Octopus Home Mini](../setup/account.md#home-mini) or have configured an [Octopus Home Pro](../setup//account.md#home-pro). Do not set unless you have one.

!!! info
    An export equivalent of this sensor does not exist because the data is not available

The total consumption reported by the meter for all time. This will try and update every minute for Home Mini and every 10 seconds for Home Pro.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

### Current Total Export

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_total_export`

!!! warning
    This will only be available if you have specified you have an [Octopus Home Mini](../setup/account.md#home-mini). Do not set unless you have one.

!!! info
    Not all meters provide this information. In these scenarios, this sensor will report zero or unknown.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

The total export reported by the meter for all time. This will try and update every minute for Home Mini.

| Attribute | Type | Description |
|-----------|------|-------------|
| `mpan` | `string` | The mpan for the associated meter |
| `serial_number` | `string` | The serial for the associated meter |
| `is_export` | `boolean` | Determines if the meter exports energy rather than imports |
| `is_smart_meter` | `boolean` | Determines if the meter is considered smart by Octopus Energy |

### Current Accumulative Cost

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_cost`

!!! warning
    This will only be available if you have specified you have an [Octopus Home Mini](../setup/account.md#home-mini). Do not set unless you have one.

!!! info
    An export equivalent of this sensor does not exist because the data is not available

!!! info
    If you are on an intelligent tariff, this will not include charges that are done outside of normal off peak hours in certain scenarios. See the [FAQ](../faq.md#im-on-an-intelligent-tariff-but-the-cost-sensors-are-out-is-this-normal) for more information around this.

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

#### Variants

The following variants of the [Current Accumulative Cost](#current-accumulative-cost) are available.

##### Off Peak

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_cost_off_peak`

The total cost reported by the meter for the current day during off peak hours (the lowest available rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

!!! warning
    This will only be available if you have specified you have a [Octopus Home Mini](../setup/account.md#home-mini) or have configured an [Octopus Home Pro](../setup//account.md#home-pro). Do not set unless you have one.

!!! warning

    If you are on intelligent and are using a provider where [planned_dispatches](./intelligent.md#is-dispatching) are not supported, then charges outside of your normal off peak periods will be counted at peak. This is because Octopus Energy doesn't provide enough information to determine if a completed dispatch was a bump charge or a planned charge.

!!! info
    An export equivalent of this sensor does not exist because the data is not available

##### Standard

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_cost_standard`

The total cost reported by the meter for the current day during standard hours (the middle rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

!!! warning
    This will only be available if you have specified you have a [Octopus Home Mini](../setup/account.md#home-mini) or have configured an [Octopus Home Pro](../setup//account.md#home-pro). Do not set unless you have one.

!!! info
    An export equivalent of this sensor does not exist because the data is not available

##### Peak

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_cost_peak`

The total cost reported by the meter for the current day during peak hours (the highest available rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

!!! warning
    This will only be available if you have specified you have a [Octopus Home Mini](../setup/account.md#home-mini) or have configured an [Octopus Home Pro](../setup//account.md#home-pro). Do not set unless you have one.

!!! info
    An export equivalent of this sensor does not exist because the data is not available

### Current Interval Accumulative Consumption

`sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_interval_accumulative_consumption`

!!! warning
    This will only be available if you have specified you have an [Octopus Home Mini](../setup/account.md#home-mini). Do not set unless you have one.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

This will indicate the total accumulative consumption for the current 30 minute period (e.g. if it's 12:15 then this will represent 12:00 - 12:30). You can use this to compare the data with the [saving session baseline](./octoplus.md#saving-session-baseline) sensor to see how on track you are during a saving session.

!!! info

    You can use the [data_last_retrieved sensor](./diagnostics.md#current-consumption-data-last-retrieved) to determine when the underlying data was last retrieved from the OE servers.