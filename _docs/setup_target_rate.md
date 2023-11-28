# Setup Target Rate Sensor(s)

- [Setup Target Rate Sensor(s)](#setup-target-rate-sensors)
  - [Setup](#setup)
    - [Target Timeframe](#target-timeframe)
      - [Agile Users](#agile-users)
    - [Hours](#hours)
    - [Offset](#offset)
    - [Rolling Target](#rolling-target)
    - [Latest Period](#latest-period)
    - [Invert Target Rates](#invert-target-rates)
  - [Attributes](#attributes)
  - [Services](#services)
  - [Examples](#examples)
    - [Continuous](#continuous)
    - [Intermittent](#intermittent)

After you've configured your [account](./setup_account.md), you'll be able to configure target rate sensors. These are configured by adding subsequent instances of the integration going through the [normal flow](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy).

These sensors calculate the lowest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active. If you are targeting an export meter, then the sensors will calculate the highest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active.

These sensors can then be used in automations to turn on/off devices that save you (and the planet) energy and money. You can go through this flow as many times as you need target rate sensors.

Each sensor will be in the form `binary_sensor.octopus_energy_target_{{TARGET_RATE_NAME}}`.

## Setup

### Target Timeframe

If you're wanting your devices to come on during a certain timeframe, for example while you're at work, you can set the minimum and/or maximum times for your target rate sensor. These are specified in 24 hour clock format and will attempt to find the optimum discovered period during these times.

The `from/start` time can be set in the field `The minimum time to start the device` and the `to/end` time can be set in the field `The maximum time to stop the device`.

If not specified, these default from `00:00:00` to `00:00:00` the following day.

If for example you want to look at prices overnight you could set the minimum time to something like `20:00` and your maximum time to something like `05:00`. If the minimum time is "before" the maximum time, then it will treat the maximum time as the time for the following day.

> Please note: The target rate will not be evaluated until **all rates** are available for the specified timeframe. Therefore if we're looking between `00:00` and `00:00`, full rate information must exist between this time. Whereas if times are between `10:00` and `16:00`, then rate information is only needed between these times before it can be calculated.

#### Agile Users

If you are an agile user, then agile prices are available from [11pm to 11pm UK time](https://developer.octopus.energy/docs/api/#agile-octopus) and published at `16:00` UK time. Therefore, you cannot specify a timeframe that starts before `16:00` and ends after `23:00` because the target rate(s) will not be able to be calculated until part way through the specified timeframe as this is when the full set will become available. We recommend you set your timeframes to `16:00`/`16:00` or `23:00`/`23:00` if you're wanting to target a full 24 hours, but other valid times might include


| from/start | to/end | Notes |
|-|-|-|
| `10:00` | `23:00` | our start time is before 4pm, but our end time is not after 11pm. |
| `16:30` | `23:30` | our start time is after 4pm, so our end time can be after 11pm. |
| `17:00` | `14:00` | our start time is after 4pm and our end time is before our start time so therefore for the next day. Doing this might delay when the target rate sensor is calculated depending on when the rates are made available for the next day (e.g. if they're late for publishing). |

This is not automatically done by the integration as I didn't want to cause confusion for users when they didn't set anything nor did I want behaviour to implicitly change when users switch tariffs.

See the examples below for how this can be used and how rates will be selected.

### Hours

The hours that you require for the sensor to find. This should be in decimal format and represent 30 minute increments. For example 30 minutes would be `0.5`, 1 hour would be `1` or `1.0`, 1 hour and 30 minutes would be `1.5`, etc.

### Offset

You may want your target rate sensors to turn on a period of time before the optimum discovered period. For example, you may be turning on a robot vacuum cleaner for a 30 minute clean and want it to charge during the optimum period. For this, you'd use the `offset` field and set it to `-00:30:00`, which can be both positive and negative and go up to a maximum of 24 hours. This will shift when the sensor turns on relative to the optimum period. For example, if the optimum period is between `2023-01-18T10:00` and `2023-01-18T11:00` with an offset of `-00:30:00`, the sensor will turn on between `2023-01-18T09:30` and `2023-01-18T10:30`.

### Rolling Target

Depending on how you're going to use the sensor, you might want the best period to be found throughout the day so it's always available. For example, you might be using the sensor to turn on a washing machine which you might want to come on at the best time regardless of when you use the washing machine. This can result in the sensor coming on more than the target hours, and therefore should be used in conjuction with other sensors. You can activate this behaviour by setting the `Re-evaluate multiple times a day` checkbox.

However, you might also only want the target time to occur once a day so once the best time for that day has passed it won't turn on again. For example, you might be using the sensor to turn on something that isn't time critical and could wait till the next day like a charger. This is the default behaviour and is done by not setting the `Re-evaluate multiple times a day` checkbox.

### Latest Period

Depending on how you're going to use the sensor, you might want the best period at the latest possible time. For example, you might be using the sensor to turn on an immersion heater which you'll want to come on at the end of the cheapest found period. 

For instance if you turn this on and the cheapest period is between `2023-01-01T00:30` and `2023-01-01T05:00` and your target rate is for 1 hour, then it will come on between `2023-01-01T04:00` and `2023-01-01T05:00` instead of `2023-01-01T00:30` and `2023-01-01T01:30`.

This feature is toggled on by the `Find last applicable rates` checkbox.

### Invert Target Rates

If this is checked, then the normal behaviour of the sensor will be reversed. This means if you target an **import** sensor, with this checked it will find the most expensive rates. Similarly if you target an **export** meter, with this checked it will find the cheapest rates.

## Attributes

The following attributes are available on each sensor

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `string` | The name of the sensor. |
| `hours` | `string` | The total hours are being discovered.  |
| `type` | `string` | The type/mode for the target rate sensor. This will be either `continuous` or `intermittent`. |
| `mpan` | `string` | The `mpan` of the meter being used to determine the rates. |
| `rolling_target` | `boolean` | Determines if `Re-evaluate multiple times a day` is turned on for the sensor. |
| `last_rates` | `boolean` | Determines if `Find last applicable rates` is turned off for the sensor. |
| `offset` | `string` | The offset configured for the sensor. |
| `start_time` | `string` | The start time configured for the sensor. |
| `end_time` | `string` | The end time configured for the sensor. |
| `is_target_export` | `boolean` | Determines if the meter being targeted is exporting energy. This will change the behaviour of the sensor to look for the highest rates. |
| `target_times` | `list` | The discovered times and rates the sensor will come on for. |
| `overall_average_cost` | `float` | The average cost/rate of all discovered times during the current **24 hour period**. |
| `overall_min_cost` | `float` | The minimum cost/rate of all discovered times during the current **24 hour period**. |
| `overall_max_cost` | `float` | The maximum cost/rate of all discovered times during the current **24 hour period**. |
| `current_duration_in_hours` | `float` | The duration the sensor will be on for, for the current continuous discovered period. For `continuous` sensors, this will be the entire period. For `intermittent` sensors, this could be the entire period or a portion of it, depending on the discovered times. This could be `none`/`unknown` if the sensor is not currently in a discovered period. |
| `current_average_cost` | `float` | The average cost/rate for the current continuous discovered period. This could be `none`/`unknown` if the sensor is not currently in a discovered period. |
| `current_min_cost` | `float` | The min cost/rate for the current continuous discovered period. This could be `none`/`unknown` if the sensor is not currently in a discovered period. |
| `current_max_cost` | `float` | The max cost/rate for the current continuous discovered period. This could be `none`/`unknown` if the sensor is not currently in a discovered period. |
| `next_time` | `datetime` | The next date/time the sensor will come on. This could be `none`/`unknown` if there are no more periods for the current **24 hour period**. |
| `next_duration_in_hours` | `float` | The duration the sensor will be on for, for the next continuous discovered period. For `continuous` sensors, this will be the entire period. For `intermittent` sensors, this could be the entire period or a portion of it, depending on the discovered times. This could be `none`/`unknown` if there are no more periods for the current **24 hour period**. |
| `next_average_cost` | `float` | The average cost/rate for the next continuous discovered period. For `continuous` sensors, this will be the entire period. For `intermittent` sensors, this could be the entire period or a portion of it, depending on the discovered times. This could be `none`/`unknown` if there are no more periods for the current **24 hour period**. |
| `next_min_cost` | `float` | The average cost/rate for the next continuous discovered period. This could be `none`/`unknown` if there are no more periods for the current **24 hour period**. |
| `next_max_cost` | `float` | The average cost/rate for the next continuous discovered period. This could be `none`/`unknown` if there are no more periods for the current **24 hour period**. |
| `target_times_last_evaluated` | datetime | The datetime the target times collection was last evaluated. This will occur if all previous target times are in the past and all rates are available for the requested future time period. For example, if you are targeting 16:00 (day 1) to 16:00 (day 2), and you only have rates up to 23:00 (day 1), then the target rates won't be calculated. |
| `last_evaluated` | `datetime` | The datetime the state of the sensor was last evaluated based on the current specified target times. This should update every minute |

## Services

There are services available associated with target rate sensors. Please review them in the [services doc](./services.md).

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
