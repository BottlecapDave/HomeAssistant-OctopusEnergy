# Target Rate Sensor(s)

!!! warning

    It has been [proposed](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/discussions/1305) that the target rate feature of the integration be deprecated and removed in favour of a new external integration, [Target Timeframes](https://bottlecapdave.github.io/HomeAssistant-TargetTimeframes/). The full reasoning can be found in the proposal.

    A [migration guide](../migrations/target_timeframes.md) is available for migrating target rate sensors to the new integration.

After you've configured your [account](./account.md), you'll be able to configure target rate sensors. These are configured by adding subsequent instances of the integration going through the [normal flow](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy), and selecting `Target Rate` in the provided menu.

These sensors calculate the lowest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active. If you are targeting an export meter, then the sensors will calculate the highest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active. If you are wanting to evaluate on a rolling basis, you might be interested in the [rolling target rate sensors](./rolling_target_rate.md)

These sensors can then be used in automations to turn on/off devices that save you (and the planet) energy and money. You can go through this flow as many times as you need target rate sensors.

Each sensor will be in the form `binary_sensor.octopus_energy_target_{{TARGET_RATE_NAME}}`.

## Setup

### Target Timeframe

If you're wanting your devices to come on during a certain timeframe, for example while you're at work, you can set the minimum and/or maximum times for your target rate sensor. These are specified in 24 hour clock format and will attempt to find the optimum discovered period during these times.

The `from/start` time can be set in the field `The minimum time to start the device` and the `to/end` time can be set in the field `The maximum time to stop the device`.

If not specified, these default from `00:00:00` to `00:00:00` the following day.

If for example you want to look at prices overnight you could set the minimum time to something like `20:00` and your maximum time to something like `05:00`. If the minimum time is "after" the maximum time, then it will treat the maximum time as the time for the following day.

!!! info

    The target rate will not be evaluated until **all rates** are available for the specified timeframe. Therefore if we're looking between `00:00` and `00:00`, full rate information must exist between this time. Whereas if times are between `10:00` and `16:00`, then rate information is only needed between these times before it can be calculated.

#### Agile Users

If you are an agile user, then agile prices are available from **11pm to 11pm UK time** and published between [`16:00` and `20:00` UK time](https://octopus.energy/smart/agile/). 

Therefore, you cannot specify a timeframe that starts before `16:00` and ends after `23:00` because the target rate(s) will not be able to be calculated until part way through the specified timeframe as this is when the full set of rate information will become available. This is best illustrated with the following example, where lets say you wanted a target rate sensor to look at between `00:00` and `00:00` the next day (24 hours). Your initial available data would potentially look like the following

| start | end | value |
| ----- | --- | ----- |
| `2023-01-01T00:00` | `2023-01-01T00:30` | 6 |
| `2023-01-01T00:30` | `2023-01-01T05:00` | 12 |
| `2023-01-01T05:00` | `2023-01-01T05:30` | 7 |
| `2023-01-01T05:30` | `2023-01-01T18:00` | 20 |
| `2023-01-01T18:00` | `2023-01-01T23:00` | 34 |

Where the last hour of data isn't available (because agile doesn't provide this data in the initial batch), which means the target rate sensor can't calculate the best time because it doesn't have the full data set available. If agile rate data for the next 24 hour period then became available at `16:30` and looked like the following

| start | end | value |
| ----- | --- | ----- |
| `2023-01-01T23:00` | `2023-01-02T00:00` | 19 |

We now have the full data set available for the target rate sensor to calculate the best time, which would be done close to when the agile data became available (e.g. around `16:30`). The result would be the target rate sensor would pick `2023-01-01T00:00` to `2023-01-01T00:30` or `2023-01-01T05:00` to `2023-01-01T05:30` because these are the cheapest times. However, these times are in the past because we're now at `16:30` and so our target rate sensor will never turn on. If a time in the future was picked to counteract this, then people would question why it didn't turn on during the cheapest times.

Therefore, we recommend you set your timeframes to `16:00`/`16:00` or `23:00`/`23:00` if you're wanting to target a full 24 hours, however other valid times might include

| from/start | to/end | Notes |
|-|-|-|
| `10:00` | `23:00` | our start time is before 4pm, but our end time is not after 11pm. |
| `16:30` | `23:30` | our start time is after 4pm, so our end time can be after 11pm. |
| `17:00` | `14:00` | our start time is after 4pm and our end time is before our start time so therefore for the next day. Doing this might delay when the target rate sensor is calculated depending on when the rates are made available for the next day (e.g. if they're late for publishing). |

This is not automatically done by the integration as I didn't want to cause confusion for users when they didn't set anything nor did I want behaviour to implicitly change when users switch tariffs.

See the examples below for how this can be used and how rates will be selected.

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

### Evaluation mode

Because the time frame that is being evaluated could have external factors change the underlying data (e.g. if you're using [external rate weightings](#external-rate-weightings)), you might want to set how/when the target times are evaluated in order to make the selected times more or less dynamic.

#### All existing target rates are in the past

This is the default way of evaluating target times. This will only evaluate new target times if no target times have been calculated or all existing target times are in the past.

#### Existing target rates haven't started or finished

This will only evaluate target times if no target times have been calculated or all existing target times are either in the future or all existing target times are in the past. 

For example, lets say we have a continuous target which looks between `00:00` and `08:00` has existing target times from `2023-01-02T01:00` to `2023-01-02T02:00`. 

* If the current time is `2023-01-02T00:59`, then the target times will be re-evaluated and might change if the target period (i.e. `2023-01-02T00:30` to `2023-01-02T08:30`) has better rates than the existing target times (e.g. the external weightings have changed).
* If the current time is `2023-01-02T01:00`, the the target times will not be re-evaluated because we've entered our current target times, even if the evaluation period has cheaper times. 
* If the current time is `2023-01-02T02:01`, the the target times will be re-evaluated because our existing target times are in the past and will find the best times in the new rolling target period (i.e. `2023-01-02T02:00` to `2023-01-02T10:00`). 

### Offset

You may want your target rate sensors to turn on a period of time before the optimum discovered period. For example, you may be turning on a robot vacuum cleaner for a 30 minute clean and want it to charge during the optimum period. For this, you'd use the `offset` field and set it to `-00:30:00`, which can be both positive and negative and go up to a maximum of 24 hours. This will shift when the sensor turns on relative to the optimum period. For example, if the optimum period is between `2023-01-18T10:00` and `2023-01-18T11:00` with an offset of `-00:30:00`, the sensor will turn on between `2023-01-18T09:30` and `2023-01-18T10:30`.

### Re-evaluate within time frame

Depending on how you're going to use the sensor, you might want the best period to be found throughout the day so it's always available. For example, you might be using the sensor to turn on a washing machine which you might want to come on at the best time regardless of when you use the washing machine. You can activate this behaviour by setting the `Re-evaluate multiple times a day` checkbox.

!!! warning

    Using this can result in the sensor coming on more than the target hours, and therefore should be used in conjunction with other sensors. Depending on how long your target timeframe is, upon each re-evaluation the picked times will get steadily worse.

However, you might also only want the target time to occur once during each timeframe so once the best time for that day has passed it won't turn on again until the next timeframe. For example, you might be using the sensor to turn on something that isn't time critical and could wait till the next timeframe like a charger. This is the default behaviour and is done by not setting the `Re-evaluate multiple times a day` checkbox.

!!! info

    The next set of target times will not be calculated until all target times are in the past. This will have an effect on the `next` set of attributes on the sensor.

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
| `target_times_evaluation_mode` | `string` | The mode that determines when/how target times are picked |
| `rolling_target` | `boolean` | Determines if `Re-evaluate multiple times a day` is turned on for the sensor. |
| `last_rates` | `boolean` | Determines if `Find last applicable rates` is turned off for the sensor. |
| `offset` | `string` | The offset configured for the sensor. |
| `start_time` | `string` | The start time configured for the sensor. |
| `end_time` | `string` | The end time configured for the sensor. |
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

There are services available associated with target rate sensors. Please review them in the [services doc](../services.md#target-rates).

## Examples

Let's look at a few examples. Let's say we have the the following (unrealistic) set of rates:

| start | end | value |
| ----- | --- | ----- |
| `2023-01-01T00:00` | `2023-01-01T00:30` | 6 |
| `2023-01-01T00:30` | `2023-01-01T05:00` | 12 |
| `2023-01-01T05:00` | `2023-01-01T05:30` | 7 |
| `2023-01-01T05:30` | `2023-01-01T18:00` | 20 |
| `2023-01-01T18:00` | `2023-01-01T23:30` | 34 |
| `2023-01-01T23:30` | `2023-01-02T00:30` | 5 |
| `2023-01-02T00:30` | `2023-01-02T05:00` | 12 |
| `2023-01-02T05:00` | `2023-01-02T05:30` | 7 |
| `2023-01-02T05:30` | `2023-01-02T18:00` | 20 |
| `2023-01-02T18:00` | `2023-01-02T23:00` | 34 |
| `2023-01-02T23:30` | `2023-01-03T00:00` | 6 |

### Continuous

If we look at a continuous sensor that we want on for 1 hour.

If we set no from/to times, then our 24 hour period being looked at ranges from `00:00:00` to `23:59:59`.

The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T00:00` - `2023-01-01T01:00` | `false`                            | While 5 is our lowest rate within the current 24 hour period, it doesn't cover our whole 1 hour and is next to a high 34 rate. A rate of 6 is the next available rate with a low following rate. |
| `2023-01-01T01:00` | `2023-01-02T00:00` - `2023-01-02T01:00` | `false`                            | Our lowest period is in the past, so we have to wait until our target period has passed to look at the next evaluation period. |
| `2023-01-01T01:00` | `2023-01-01T04:30` - `2023-01-01T05:30` | `true`                             | The rate of 6 is in the past, so 7 is our next lowest rate. 12 is smaller rate than 20 so we start in the rate period before to fill our desired hour. |
| `2023-01-01T23:30` | None | `true`                             | There is no longer enough time available in the current 24 hour period, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times for `05:00` to `19:00`, we then limit the period that we look at. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T05:00` - `2023-01-01T06:00` | `false`                            | The rate of 12 is no longer available as it's outside of our `from` time. |
| `2023-01-01T06:30` | `2023-01-02T05:00` - `2023-01-02T06:00` | `false`                            | Our lowest period is in the past, so we have to wait until our target period has passed to look at the next evaluation period. |
| `2023-01-01T06:30` | `2023-01-01T06:30` - `2023-01-01T07:30` | `true`                             | The rate of 7 is in the past, so we must look for the next lowest combined rate. |
| `2023-01-01T18:00` | `2023-01-01T18:00` - `2023-01-01T19:00` | `true`                             | The rate of 20 is in the past, so we must look for the next lowest combined rate which is 34. |
| `2023-01-01T18:30` | None | `true`                            | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times to look over two days, from `20:00` to `06:00`, we then limit the period that we look at to overnight. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T20:00` | `2023-01-01T23:30` - `2023-01-02T01:30` | `false`                            | Our lowest rate of 5 now falls between our overnight time period so is available. |
| `2023-01-02T02:00` | `2023-01-01T23:30` - `2023-01-02T01:30` | `false`                            | Our lowest period is in the past, so we have to wait until our target period has passed to look at the next evaluation period. |
| `2023-01-02T02:00` | `2023-01-02T04:30` - `2023-01-02T05:30` | `true`                             | The rate of 5 is in the past, so we must look for the next lowest combined rate, which includes our half hour rate at 7. |
| `2023-01-02T05:30` | None | `true`                             | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set an offset of `-00:30:00`, then while the times might be the same, the target rate sensor will turn on 30 minutes before the select rate period starts. Any set time restrictions **will not** include the offset.

### Intermittent

If we look at an intermittent sensor that we want on for 1 hour total (but not necessarily together).

If we set no from/to times, then our 24 hour period being looked at ranges from `00:00:00` to `23:59:59`.

The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T00:00` - `2023-01-01T00:30`, `2023-01-01T23:30` - `2023-01-02T00:00` | `false`                            | Our sensor will go on for 30 minutes at the cheapest rate, then 30 minutes at the next cheapest rate. |
| `2023-01-01T01:00` | `2023-01-01T00:00` - `2023-01-01T00:30`, `2023-01-01T23:30` - `2023-01-02T00:00` | `false`                            | Our sensor will go on for 30 minutes at the cheapest rate, which will be in the past, then 30 minutes at the next cheapest rate. |
| `2023-01-01T01:00` | `2023-01-01T05:00` - `2023-01-01T05:30`, `2023-01-01T23:30` - `2023-01-02T00:00` | `true`                             | Our sensor will go on for 30 minutes at the second cheapest rate, then 30 minutes at the third cheapest rate. |
| `2023-01-01T23:30` | None | `true`                             | There is no longer enough time available in the current 24 hour period, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times for `05:00` to `19:00`, we then limit the period that we look at. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T05:00` - `2023-01-01T05:30`, `2023-01-01T05:30` - `2023-01-01T06:00` | `false`                            | Our cheapest rates are outside our target range, so we need to look at the next cheapest. Luckily on our scenario the two cheapest rates are next to each other. |
| `2023-01-01T06:30` | `2023-01-01T05:00` - `2023-01-01T05:30`, `2023-01-01T05:30` - `2023-01-01T06:00` | `false`                            | Both of our cheapest rates in the target range are in the past. |
| `2023-01-01T06:30` | `2023-01-01T06:30` - `2023-01-01T07:00`, `2023-01-01T07:00` - `2023-01-01T07:30` | `true`                             | Both of our cheapest rates in the target range are in the past, so we must look for the next lowest combined rate. |
| `2023-01-01T18:30` | None | `true`                            | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times to look over two days, from `20:00` to `06:00`, we then limit the period that we look at to overnight. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T20:00` | `2023-01-01T23:30` - `2023-01-02T00:30`, `2023-01-02T05:00` - `2023-01-02T05:30` | `false`                            | Our lowest rate of 5 now falls between our overnight time period so is available. |
| `2023-01-02T02:00` | `2023-01-01T23:30` - `2023-01-02T00:30`, `2023-01-02T05:00` - `2023-01-02T05:30` | `false`                            | Our lowest period is in the past, but we still have a rate in the future so our sensor will only come on once. |
| `2023-01-02T02:00` | `2023-01-02T02:00` - `2023-01-02T02:30`, `2023-01-02T05:00` - `2023-01-02T05:30` | `true`                             | The rate of 5 is in the past, so we must look for the next lowest combined rate, which includes our half hour rate at 7. |
| `2023-01-02T05:30` | None | `true`                             | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set an offset of `-00:30:00`, then while the times might be the same, the target rate sensor will turn on 30 minutes before the select rate period starts. Any set time restrictions **will not** include the offset.
