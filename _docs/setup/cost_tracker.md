# Cost Tracker Sensor(s)

Ever wondered how much your individual appliances are costing you? You can create a cost tracker that monitors the consumption of an existing sensor and calculates the daily cost based on your tariff. You can also use these sensors to track the money you're making potentially from exports.

!!! info

    The cost is only calculated when the monitored sensor changes. Therefore the accuracy of the cost tracker sensors is dependent on the frequency the monitored entity updates.

## Setup

After you've configured your [account](./account.md), you'll be able to configure cost tracker sensors. These are configured by adding subsequent instances of the integration going through the [normal flow](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy), and selecting `Cost Tracker` in the provided menu.

### Name

This is the unique name for the cost trackers

### Meter

This is the meter whose tariff will determine the rate the entity consumption is calculated at. This can be either an import or export based meter, meaning that you can track the money you're potentially making from your exports. 

### Entity

This is the entity whose consumption should be tracked and the cost calculated against. This entity will be assumed to be reporting `kwh`, unless stated otherwise.

### Tracked entity state is accumulative

This should be true if the tracked entity's state increases over time (true) or if it's the raw value (false).

!!! info

    If you are tracking a "total_increasing" sensor, then based on [HA documentation](https://developers.home-assistant.io/docs/core/entity/sensor#available-state-classes) any decrease in value will be treated as a reset and the new state will be recorded as is. 
    
    However, there have [been reports](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/901) of some sensors misbehaving. To counteract this, if there is less than a 10% decrease, then the difference between the new and old state will be recorded.

### Don't automatically reset the cost sensor

By default, the sensor will automatically reset when a new reading has been received and it's a different day to the previous reading. There may be times that you want to track costs for something over this threshold (e.g. how much it last cost you to charge your car). In these scenarios, you can turn off the automatic resets. In this scenario, you are in charge of resetting the core sensor via it's [available service](../services.md#octopus_energyreset_cost_tracker).

!!! info

    The weekly and monthly sensors will reset as normal with this settings turned on.

!!! warning

    Not resetting this sensor for long periods of time can cause Home Assistant warnings around recording of state. This results in the attributes of the sensor not being persisted to the database for long term storage. This is a known limitation of the feature and cannot be fixed due to how the sensor tracks cost.

### Week sensor day reset

This is the day of the week the accumulative week sensor should reset. This defaults to Monday.

### Month sensor day reset

This is the day of the month the accumulative month sensor should reset. This must be between 1 and 28 (inclusively). This defaults to the 1st.

## Handling Exporting

Due to everyone's HA setup being different for how they track importing/exporting, the sensors themselves assume that all consumption changes should be tracked and the cost calculated. However, you may wish to turn off tracking when you're exporting. This can be done via the related [services](../services.md#octopus_energyupdate_cost_tracker).

## Entities

### Cost sensor

`sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}`

This is the total cost of the tracked entity for the current day.

This is in pounds and pence (e.g. 1.01 = £1.01).

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `string` | The base name of the cost tracker (based on config) |
| `mpan` | `string` | The mpan of the meter that determines how the cost is calculated (based on config) |
| `target_entity_id` | `string` | The entity whose consumption data is being tracked (based on config) |
| `entity_accumulative_value` | `boolean` | Determines if the tracked entity has accumulative data (based on config) |
| `account_id` | `string` | The id of the account the cost tracker is for (based on config) |
| `is_manual` | `boolean` | Determines if the tracker only resets when manually reset via the available service |
| `is_tracking` | `boolean` | Determines if the tracker is currently tracking consumption/cost data |
| `tracked_changes` | `array` | The collection of tracked entity changes where the costs have been tracked in 30 minute increments |
| `untracked_changes` | `array` | The collection of tracked entity changes where the costs have **not** been tracked in 30 minute increments |
| `total_consumption` | `float` | The total consumption that has been tracked for the current day |

Each item within the `tracked_changes` and `untracked_changes` have the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the consumption starts |
| `end` | `datetime` | The date/time when the consumption ends |
| `rate` | `float` | The rate the consumption is charged at. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `consumption` | `float` | The consumption value of the specified period. This will be in `kwh`. |
| `cost` | `float` | The cost of the consumption at the specified rate. This is in pounds and pence (e.g. 1.01 = £1.01) |
| `cost_raw` | `float` | The raw cost of the consumption at the specified rate. This is in pounds and pence, but not rounded. This is to account for low cost devices |

#### Variants

The following variants of the [Cost Sensor](#cost-sensor) are available.

##### Off Peak

`sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_off_peak`

This is the total cost of the tracked entity for the current day during off peak hours (the lowest available rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

!!! warning

    If you are on intelligent and are using a provider where [planned_dispatches](../entities/intelligent.md#is-dispatching) are not supported, then charges outside of your normal off peak periods will be counted at peak. This is because Octopus Energy doesn't provide enough information to determine if a completed dispatch was a bump charge or a planned charge.

##### Standard

`sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_standard`

This is the total cost of the tracked entity for the current day during standard hours (the middle rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

##### Peak

`sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_peak`

This is the total cost of the tracked entity for the current day during peak hours (the highest available rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

### Week cost sensor

`sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_week`

This is the total cost of the tracked entity for the current week. This will reset on the configured day.

This is in pounds and pence (e.g. 1.01 = £1.01).

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `string` | The base name of the cost tracker (based on config) |
| `mpan` | `string` | The mpan of the meter that determines how the cost is calculated (based on config) |
| `target_entity_id` | `string` | The entity whose consumption data is being tracked (based on config) |
| `entity_accumulative_value` | `boolean` | Determines if the tracked entity has accumulative data (based on config) |
| `account_id` | `string` | The id of the account the cost tracker is for (based on config) |
| `accumulated_data` | `array` | The collection of accumulated cost in daily increments |
| `total_consumption` | `float` | The total consumption that has been tracked for the current week |

Each item within the `accumulated_data` has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the consumption starts |
| `end` | `datetime` | The date/time when the consumption ends |
| `consumption` | `float` | The consumption value of the specified period. This will be in `kwh`. |
| `cost` | `float` | The cost of the consumption at the specified rate. This is in pounds and pence (e.g. 1.01 = £1.01) |

#### Variants

The following variants of the [Week Cost Sensor](#week-cost-sensor) are available.

##### Off Peak

`sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_week_off_peak`

This is the total cost of the tracked entity for the current week during off peak hours (the lowest available rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

!!! warning

    If you are on intelligent and are using a provider where [planned_dispatches](../entities/intelligent.md#is-dispatching) are not supported, then charges outside of your normal off peak periods will be counted at peak. This is because Octopus Energy doesn't provide enough information to determine if a completed dispatch was a bump charge or a planned charge.

##### Standard

`sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_week_standard`

This is the total cost of the tracked entity for the current week during standard hours (the middle rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

##### Peak

`sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_week_peak`

This is the total cost of the tracked entity for the current week during peak hours (the highest available rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

### Month cost sensor

`sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_month`

This is the total cost of the tracked entity for the current month. This will reset on the configured day.

This is in pounds and pence (e.g. 1.01 = £1.01).

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `string` | The base name of the cost tracker (based on config) |
| `mpan` | `string` | The mpan of the meter that determines how the cost is calculated (based on config) |
| `target_entity_id` | `string` | The entity whose consumption data is being tracked (based on config) |
| `entity_accumulative_value` | `boolean` | Determines if the tracked entity has accumulative data (based on config) |
| `account_id` | `string` | The id of the account the cost tracker is for (based on config) |
| `accumulated_data` | `array` | The collection of accumulated cost in daily increments |
| `total_consumption` | `float` | The total consumption that has been tracked for the current month |

Each item within the `accumulated_data` has the following attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | The date/time when the consumption starts |
| `end` | `datetime` | The date/time when the consumption ends |
| `consumption` | `float` | The consumption value of the specified period. This will be in `kwh`. |
| `cost` | `float` | The cost of the consumption at the specified rate. This is in pounds and pence (e.g. 1.01 = £1.01) |

#### Variants

The following variants of the [Month Cost Sensor](#month-cost-sensor) are available.

##### Off Peak

`sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_month_off_peak`

This is the total cost of the tracked entity for the current month during off peak hours (the lowest available rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

!!! warning

    If you are on intelligent and are using a provider where [planned_dispatches](../entities/intelligent.md#is-dispatching) are not supported, then charges outside of your normal off peak periods will be counted at peak. This is because Octopus Energy doesn't provide enough information to determine if a completed dispatch was a bump charge or a planned charge.

##### Standard

`sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_month_standard`

This is the total cost of the tracked entity for the current month during standard hours (the middle rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

##### Peak

`sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_month_peak`

This is the total cost of the tracked entity for the current month during peak hours (the highest available rate).

!!! note
    This is only available when on a tariff with 2 or 3 unique rates during a given day. 
    
    If you switch to a tariff that meets this criteria, you will need to reload the integration to gain access to this entity.

    If you switch to a tariff that no longer meets this criteria, the entity will no longer be updated. When you reload the integration, this entity will no longer be available.

    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

## Services

There are services available associated with cost tracker sensors. Please review them in the [services doc](../services.md#cost-trackers).