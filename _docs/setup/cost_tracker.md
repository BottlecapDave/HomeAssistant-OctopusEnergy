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

This is the entity whose consumption should be tracked and the cost calculated against. This entity should be reporting in `kwh`.

### Tracked entity state is accumulative

This should be true if the tracked entity's state increases over time (true) or if it's the difference between updates (false).

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
| `consumption` | `float` | The consumption value of the specified period |
| `cost` | `float` | The cost of the consumption at the specified rate. This is in pounds and pence (e.g. 1.01 = £1.01) |

### Cost sensor (Peak)

`sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_peak`

This is the total cost of the tracked entity at peak rate for the current day. This is in pounds and pence (e.g. 1.01 = £1.01).

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `string` | The base name of the cost tracker (based on config) |
| `mpan` | `string` | The mpan of the meter that determines how the cost is calculated (based on config) |
| `target_entity_id` | `string` | The entity whose consumption data is being tracked (based on config) |
| `entity_accumulative_value` | `boolean` | Determines if the tracked entity has accumulative data (based on config) |
| `account_id` | `string` | The id of the account the cost tracker is for (based on config) |
| `is_tracking` | `boolean` | Determines if the tracker is currently tracking consumption/cost data |
| `total_consumption` | `float` | The total consumption that has been tracked for the current day at peak rate |

### Cost sensor (Off Peak)

`sensor.octopus_energy_cost_tracker_{{COST_TRACKER_NAME}}_off_peak`

This is the total cost of the tracked entity at off peak rate for the current day. This is in pounds and pence (e.g. 1.01 = £1.01).

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them).

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `string` | The base name of the cost tracker (based on config) |
| `mpan` | `string` | The mpan of the meter that determines how the cost is calculated (based on config) |
| `target_entity_id` | `string` | The entity whose consumption data is being tracked (based on config) |
| `entity_accumulative_value` | `boolean` | Determines if the tracked entity has accumulative data (based on config) |
| `account_id` | `string` | The id of the account the cost tracker is for (based on config) |
| `is_tracking` | `boolean` | Determines if the tracker is currently tracking consumption/cost data |
| `total_consumption` | `float` | The total consumption that has been tracked for the current day at off peak rate |

## Services

There are services available associated with cost tracker sensors. Please review them in the [services doc](../services.md#octopus_energyupdate_cost_tracker).