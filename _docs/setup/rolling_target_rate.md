# Rolling Target Rate Sensor(s)

!!! warning

    It has been [proposed](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/discussions/1305) that the rolling target rate feature of the integration be deprecated and removed in favour of a new external integration, [Target Timeframes](https://bottlecapdave.github.io/HomeAssistant-TargetTimeframes/). The full reasoning can be found in the proposal.

    A [migration guide](../migrations/target_timeframes.md) is available for migrating rolling target rate sensors to the new integration.

After you've configured your [account](./account.md), you'll be able to configure rolling target rate sensors. These are configured by adding subsequent instances of the integration going through the [normal flow](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy), and selecting `Rolling Target Rate` in the provided menu.

These sensors calculate the lowest continuous or intermittent rates within the next available `x` hours, where `x` is configurable via the sensor, and turn on when these periods are active. If you are targeting an export meter, then the sensors will calculate the highest continuous or intermittent rates within the next available `x` hours and turn on when these periods are active. If you are wanting to evaluate on a fixed basis (e.g. every 24 hours), you might be interested in the [standard target rate sensors](./target_rate.md)

These sensors can then be used in automations to turn on/off devices that save you (and the planet) energy and money. You can go through this flow as many times as you need rolling target rate sensors.

Each sensor will be in the form `binary_sensor.octopus_energy_rolling_target_{{TARGET_RATE_NAME}}`.

## Setup

### Hours

The hours that you require for the sensor to find. This should be in decimal format and represent 30 minute increments. For example 30 minutes would be `0.5`, 1 hour would be `1` or `1.0`, 1 hour and 30 minutes would be `1.5`, etc.

### Hours Mode

There are three different modes that the target rate sensor can be set to, which determines how the specified hours should be interpreted

#### Exact (default)

The target rate sensor will try to find the best times for the specified hours. If less than the target hours are discovered, the sensor will not come on at all. If there are more hours than required that meet the specified requirements (e.g. below a certain rate), then it will come on for the cheapest available times up to the specified hours.

For instance if the cheapest period is between `2023-01-01T00:30` and `2023-01-01T05:00` and your target rate is for 1 hour, then it will come on between  `2023-01-01T00:30` and `2023-01-01T01:30`. If the available times are between `2023-01-01T00:30` and `2023-01-01T01:00`, then the sensor will not come on at all.

#### Minimum

The target rate sensor will try to find the best times for the specified hours. If less than the target hours are discovered, the sensor will not come on at all. If there are more hours than required that meet the specified requirements (e.g. below a certain rate), then it will come on for all discovered times.

For instance if the cheapest period is between `2023-01-01T00:30` and `2023-01-01T05:00` and your target rate is for 1 hour, then it will come on between  `2023-01-01T00:30` and `2023-01-01T05:00`. If the available times are between `2023-01-01T00:30` and `2023-01-01T01:00`, then the sensor will not come on at all.

#### Maximum

The target rate sensor will try to find the best times for the specified hours. If less than the target hours are discovered, the sensor will come on for all times that are discovered. If there are more hours than required that meet the specified requirements (e.g. below a certain rate), then it will come on for the cheapest available times up to the specified hours.

For instance if the cheapest period is between `2023-01-01T00:30` and `2023-01-01T05:00` and your target rate is for 1 hour, then it will come on between  `2023-01-01T00:30` and `2023-01-01T01:30`. If the available times are between `2023-01-01T00:30` and `2023-01-01T01:00`, then the sensor will come on between  `2023-01-01T00:30` and `2023-01-01T01:00`.

### Look Ahead Hours

This is the number of hours to look ahead for the best time periods. This will include the current time period. For instance, if it's `2023-01-01T00:15` and you have your look ahead hours set to `8`, then it will look for the best times between `2023-01-01T00:00` and `2023-01-01T08:00`.

### Evaluation mode

Because the time frame that is being evaluated is currently moving, you might want to set how/when the target times are evaluated in order to make the selected times more or less dynamic.

#### All existing target rates are in the past

This is the default way of evaluating target times. This will only evaluate new target times if no target times have been calculated or all existing target times are in the past.

#### Existing target rates haven't started or finished

This will only evaluate target times if no target times have been calculated or all existing target times are either in the future or all existing target times are in the past. 

For example, lets say we have a continuous rolling target which looks ahead for `8` hours and has existing target times from `2023-01-02T01:00` to `2023-01-02T02:00`. 

* If the current time is `2023-01-02T00:59`, then the target times will be re-evaluated and might change if the new rolling target period (i.e. `2023-01-02T00:30` to `2023-01-02T08:30`) has better times than the existing target times.
* If the current time is `2023-01-02T01:00`, the the target times will not be re-evaluated because we've entered our current target times, even if the new rolling target period has cheaper times. 
* If the current time is `2023-01-02T02:01`, the the target times will be re-evaluated because our existing target times are in the past and will find the best times in the new rolling target period (i.e. `2023-01-02T02:00` to `2023-01-02T10:00`). 

#### Always

This will always evaluate the best target times for the rolling target period, even if the sensor is in the middle of an existing target time period.

For example, lets say we have a continuous rolling target which looks ahead for `8` hours and has existing target times from `2023-01-02T01:00` to `2023-01-02T02:00`. 

* If the current time is `2023-01-02T00:59`, then the target times will be re-evaluated and might change if the new rolling target period (i.e. `2023-01-02T00:30` to `2023-01-02T08:30`) has better times than the existing target times.
* If the current time is `2023-01-02T01:31`, then the target times will be re-evaluated and might change if the new rolling target period (i.e. `2023-01-02T01:30` to `2023-01-02T09:30`) has better times than the existing target times.
* If the current time is `2023-01-02T02:01`, the the target times will be re-evaluated because our existing target times are in the past and will find the best times in the new rolling target period (i.e. `2023-01-02T02:00` to `2023-01-02T10:00`). 

!!! warning

    This setting means that you could end up with the sensor not turning on for the fully requested hours as the target times might be moved ahead half way through the picked times. It also could mean that the sensor doesn't come on at all during the requested look ahead hours (e.g. 8) because the cheapest period kept moving back. 

### Offset

You may want your target rate sensors to turn on a period of time before the optimum discovered period. For example, you may be turning on a robot vacuum cleaner for a 30 minute clean and want it to charge during the optimum period. For this, you'd use the `offset` field and set it to `-00:30:00`, which can be both positive and negative and go up to a maximum of 24 hours. This will shift when the sensor turns on relative to the optimum period. For example, if the optimum period is between `2023-01-18T10:00` and `2023-01-18T11:00` with an offset of `-00:30:00`, the sensor will turn on between `2023-01-18T09:30` and `2023-01-18T10:30`.

### Latest Period

Depending on how you're going to use the sensor, you might want the best period at the latest possible time. For example, you might be using the sensor to turn on an immersion heater which you'll want to come on at the end of the cheapest found period. 

For instance if you turn this on and the cheapest period is between `2023-01-01T00:30` and `2023-01-01T05:00` and your target rate is for 1 hour, then it will come on between `2023-01-01T04:00` and `2023-01-01T05:00` instead of `2023-01-01T00:30` and `2023-01-01T01:30`.

This feature is toggled on by the `Find last applicable rates` checkbox.

### Invert Target Rates

If this is checked, then the normal behaviour of the sensor will be reversed. This means if you target an **import** sensor, with this checked it will find the most expensive rates. Similarly if you target an **export** meter, with this checked it will find the cheapest rates.

### Minimum/Maximum Rates

There may be times that you want the target rate sensors to not take into account rates that are above or below a certain value (e.g. you don't want the sensor to turn on when rates go crazy or where it would be more beneficial to export). This is configured in pounds and pence format (e.g. 0.12 for 12p).

!!! info

    If hours mode is set to **minimum**, then a minimum and/or maximum rate must be specified in order for the target rate sensor to know what the cut off is for discovered times.

### Weighting

!!! info

    This is only available for **continuous** target rate sensors in **exact** hours mode.

There may be times when the device you're wanting the target rate sensor to turn on doesn't have a consistent power draw. You can specify a weighting which can be applied to each discovered 30 minute slot. This can be specified in a few different ways. Take the following example weighting for a required 2 hours.

* `1,1,2,1` - This applies a weighting of 1 to the first, second and forth slot and a weighting of 2 to the third slot. This will try and make the cheapest slot fall on the third slot, as long as the surrounding slots are cheaper than other continuous slots.
* `*,2,1` - This applies a weighting of 1 to the first, second and forth slot and a weighting of 2 to the third slot. The `*` can be used as a placeholder for the standard weighting of 1 for all slots before the ones specified.
* `1,1,2,*` - This applies a weighting of 1 to the first, second and forth slot and a weighting of 2 to the third slot. The `*` can be used as a placeholder for the standard weighting of 1 for all slots after the ones specified.
* `2,*,2` - This applies a weighting of 2 to the first and forth slot and a weighting of 1 to all slots in between. The `*` can be used as a placeholder for the standard weighting of 1 for all slots in between the specified slots.

Each slot weighting must be a whole number or decimal number and be positive.

You can also use weightings to ignore slots. This can be done by assigning a value of 0 for the desired slot.

### Free Electricity Weighting

If you subscribed to Octopus Energy's [free electricity sessions](../entities/octoplus.md#free-electricity-sessions), then you might want your sensor to favour the hours that these are available, but potentially still favour other times if they're cheaper by a larger portion. Here is where you can have a weighting applied to the rate during free electricity sessions to have them favour them in certain scenarios.

For example, if we have the following rates

| Start | End | Rate | Is Free Electricity Period |
|-|-|-|-|
| `2024-11-26 10:00:00` | `2024-11-26 10:30:00` | 0.1p | N |
| `2024-11-26 10:30:00` | `2024-11-26 11:00:00` | 0.1p | N |
| `2024-11-26 11:00:00` | `2024-11-26 11:30:00` | 0.2p | Y |
| `2024-11-26 11:30:00` | `2024-11-26 12:00:00` | 0.2p | Y |
| `2024-11-26 12:00:00` | `2024-11-26 12:30:00` | 0.3p | N |
| `2024-11-26 12:30:00` | `2024-11-26 13:00:00` | 0.3p | N |

If we had a target rate sensor of 1 hour, the following would occur with the following weightings

| Weighting | Period | Reason |
| 1 | `2024-11-26 10:00:00`-`2024-11-26 11:00:00` | Cheapest period |
| 0.5 | `2024-11-26 10:00:00`-`2024-11-26 11:00:00` | Cheapest period would be 0.1p, free electricity period would be 0.1p. By default, target rates favour the earliest sessions. |
| 0.2 | `2024-11-26 11:00:00`-`2024-11-26 12:00:00` | Cheapest period would be 0.1p, free electricity period would be 0.02p. |
| 0 | `2024-11-26 11:00:00`-`2024-11-26 12:00:00` | Cheapest period would be 0.1p, free electricity period would be 0p. This will always go for free electricity sessions if available. |

## External Rate Weightings

There may be times when you want to calculate the best times using factors that are external to data available via the integration, like grid carbon intensity or solar forecasts. This is where external rate weightings come in. Using the [Register Rate Weightings service](../services.md#octopus_energyregister_rate_weightings), you can configured weightings against given rates which are then multiplied against the associated rate. For example if you have a weighting of `2` set and a rate of `0.20`, then the rate will be interpreted as `0.40` during calculation. 

These weightings are used in addition to any [weightings](#weighting) configured against the sensor and [free electricity weightings](#free-electricity-weighting). For example if you have rate weight of `2`, a rate of `0.20`, a sensor weight of `3` and free electricity weight of `0.5`, then rate will be interpreted as `0.6` (2 * 0.20 * 3 * 0.5).

## Attributes

The following attributes are available on each sensor

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `string` | The name of the sensor. |
| `hours` | `string` | The total hours are being discovered.  |
| `type` | `string` | The type/mode for the target rate sensor. This will be either `continuous` or `intermittent`. |
| `mpan` | `string` | The `mpan` of the meter being used to determine the rates. |
| `look_ahead_hours` | `float` | The number of hours the sensor should look ahead for the best time period |
| `target_times_evaluation_mode` | `string` | The mode that determines when/how target times are picked |
| `last_rates` | `boolean` | Determines if `Find last applicable rates` is turned off for the sensor. |
| `offset` | `string` | The offset configured for the sensor. |
| `is_target_export` | `boolean` | Determines if the meter being targeted is exporting energy. This will change the behaviour of the sensor to look for the highest rates. |
| `rates_incomplete` | `boolean` | True if rate information is incomplete and therefore target times cannot be calculated; False otherwise. |
| `target_times` | `array` | The discovered times and rates the sensor will come on for. |
| `overall_average_cost` | `float` | The average cost/rate of all discovered times during the current **24 hour period**. |
| `overall_min_cost` | `float` | The minimum cost/rate of all discovered times during the current **24 hour period**. |
| `overall_max_cost` | `float` | The maximum cost/rate of all discovered times during the current **24 hour period**. |
| `current_duration_in_hours` | `float` | The duration the sensor will be on for, for the current continuous discovered period. For `continuous` sensors, this will be the entire period. For `intermittent` sensors, this could be the entire period or a portion of it, depending on the discovered times. This could be `none`/`unknown` if the sensor is not currently in a discovered period. |
| `current_average_cost` | `float` | The average cost/rate for the current continuous discovered period. This could be `none`/`unknown` if the sensor is not currently in a discovered period. |
| `current_min_cost` | `float` | The min cost/rate for the current continuous discovered period. This could be `none`/`unknown` if the sensor is not currently in a discovered period. |
| `current_max_cost` | `float` | The max cost/rate for the current continuous discovered period. This could be `none`/`unknown` if the sensor is not currently in a discovered period. |
| `next_time` | `datetime` | The next date/time the sensor will come on. This will only be populated if `target_times` has been calculated and at least one period/block is in the future. |
| `next_duration_in_hours` | `float` | The duration the sensor will be on for, for the next continuous discovered period. For `continuous` sensors, this will be the entire period. For `intermittent` sensors, this could be the entire period or a portion of it, depending on the discovered times. This will only be populated if `target_times` has been calculated and at least one period/block is in the future. |
| `next_average_cost` | `float` | The average cost/rate for the next continuous discovered period. For `continuous` sensors, this will be the entire period. For `intermittent` sensors, this could be the entire period or a portion of it, depending on the discovered times. This will only be populated if `target_times` has been calculated and at least one period/block is in the future. |
| `next_min_cost` | `float` | The average cost/rate for the next continuous discovered period. This will only be populated if `target_times` has been calculated and at least one period/block is in the future. |
| `next_max_cost` | `float` | The average cost/rate for the next continuous discovered period. This will only be populated if `target_times` has been calculated and at least one period/block is in the future. |
| `target_times_last_evaluated` | datetime | The datetime the target times collection was last evaluated. This will occur if all previous target times are in the past and all rates are available for the requested future time period. For example, if you are targeting 16:00 (day 1) to 16:00 (day 2), and you only have rates up to 23:00 (day 1), then the target rates won't be calculated. |

## Services

There are services available associated with target rate sensors. Please review them in the [services doc](../services.md#rolling-target-rates).
