# Home Assistant Octopus Energy

- [Home Assistant Octopus Energy](#home-assistant-octopus-energy)
  - [How to install](#how-to-install)
    - [HACS](#hacs)
  - [How to setup](#how-to-setup)
    - [Your account](#your-account)
      - [Home Mini](#home-mini)
      - [Calorific Value](#calorific-value)
      - [Government Pricing Caps](#government-pricing-caps)
      - [Saving Sessions](#saving-sessions)
    - [Target Rates](#target-rates)
      - [From and To times](#from-and-to-times)
      - [Offset](#offset)
      - [Rolling Target](#rolling-target)
      - [Examples](#examples)
        - [Continuous](#continuous)
        - [Intermittent](#intermittent)
    - [Gas Meters](#gas-meters)
  - [Services](#services)
    - [Service octopus\_energy.update\_target\_config](#service-octopus_energyupdate_target_config)
  - [UI](#ui)
    - [Upcoming Prices](#upcoming-prices)
  - [Increase Home Assistant logs](#increase-home-assistant-logs)
  - [FAQ](#faq)
    - [Data in my Home Assistant energy dashboard reported by Octopus Home Mini differs to Octopus Energy dashboard. Why is this?](#data-in-my-home-assistant-energy-dashboard-reported-by-octopus-home-mini-differs-to-octopus-energy-dashboard-why-is-this)
    - [Can I add the sensors to the Energy dashboard?](#can-i-add-the-sensors-to-the-energy-dashboard)
      - [I have an Octopus Home Mini](#i-have-an-octopus-home-mini)
      - [I don't have an Octopus Home Mini](#i-dont-have-an-octopus-home-mini)
    - [Why is my gas sensor reporting m3 when Octopus Energy reports it as kWh?](#why-is-my-gas-sensor-reporting-m3-when-octopus-energy-reports-it-as-kwh)
    - [I have sensors that are missing](#i-have-sensors-that-are-missing)
    - [My gas consumption/costs seem out](#my-gas-consumptioncosts-seem-out)

Custom component built from the ground up to bring your Octopus Energy details into Home Assistant to help you towards a more energy efficient (and or cheaper) home. This integration is built against the API provided by Octopus Energy UK and has not been tested for any other countries. 

This integration is in no way affiliated with Octopus Energy.

If you find this useful and are planning on moving to Octopus Energy, why not use my [referral link](https://share.octopus.energy/gray-jade-372)?

## How to install

You should take the latest [published release](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/releases). The current state of `develop` will be in flux and therefore possibly subject to change.

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation. Once installed, don't forget to restart your home assistant instance for the integration to be picked up.

### HACS

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

This integration can be installed directly via HACS.

## How to setup

Setup is done entirely via the [integration UI](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy).

### Your account

When you setup your account, you will get a few sensors. 

You'll get the following sensors for each electricity meter with an active agreement:

* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_rate` - The rate of the current 30 minute period that energy consumption is charged at (including VAT).
* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_rate` - The rate of the previous 30 minute period that energy consumption was charged at (including VAT).
* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption` - The total consumption reported by the meter for the previous day.
* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost` - The total cost for the previous day, including the standing charge.

If you export energy, then in addition you'll gain the above sensors with the name `export` present. E.g. `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_export_current_rate`.

You'll get the following sensors for each gas meter with an active agreement:

* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_rate` - The rate of the current day that gas consumption is charged at (including VAT).
* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption` - The total consumption reported by the meter for the previous day in m3. If your meter reports in m3, then this will be an accurate value reported by Octopus, otherwise it will be a calculated value.
* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption_kwh` - The total consumption reported by the meter for the previous day in kwh. If your meter reports in kwh, then this will be an accurate value reported by Octopus, otherwise it will be a calculated value.
* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_cost` - The total cost for the previous day, including the standing charge.

While you can add these sensors to the [energy dashboard](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/), because Octopus doesn't provide live consumption data, it will be off by a day and be a single block of consumption/cost.

By default, it's not possible to include current consumption sensors. This is due to Octopus Energy only receive data from the smart meters up to the previous day.

#### Home Mini

If you are lucky enough to own and [Octopus Home Mini](https://octopus.energy/blog/octopus-home-mini/), you can now receive this data within Home Assistant. When setting up (or editing) your account within Home Assistant, you will need to check the box next to `I have a Home Mini`. This will gain the following sensors which can be added to the  [energy dashboard](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/):

* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_consumption` - The latest consumption sent to Octopus Energy. By default, this will update every minute, but if this is missed then an attempt will be made to retrieve missing data. This has been built to see the accumulation within the energy dashboard. If you are wanting a sensor to see the current day's accumulation, then you will need to use something like [utility meter](https://www.home-assistant.io/integrations/utility_meter/). It has been noticed that daily consumption reported in Home Assistant can differ to when looking at past data within Octopus Energy. It looks like this is because Octopus Energy will favour "official" data from your smart meter over the data they collect.
* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_demand` - The current demand reported by the Home Mini. This will try and update every minute.

#### Calorific Value

When calculating gas costs, a calorific value is included in the calculation. Unfortunately this changes from region to region and is not provided by the Octopus Energy API. The default value of this is `40`, but if you check your latest bill you should be able to find the value for you. This will give you a more accurate consumption and cost calculation when your meter reports in `m3`.

#### Government Pricing Caps

There has been inconsistencies across tariffs on whether government pricing caps are included or not. Therefore the ability to configure pricing caps has been added within you account. Please note that while rates are reflected straight away, consumption based sensors may take up to 24 hours to reflect. This is due to how they look at data and cannot be changed. 

#### Saving Sessions

To support Octopus Energy's [saving sessions](https://octopus.energy/saving-sessions/), the following entities are available

* `octopus_energy_saving_session_points` - Supplies the points earned through the saving sessions
* `octopus_energy_saving_sessions` - Binary sensor to indicate if a saving session that the account has joined is active. Also supplies the list of joined events including future events.

### Target Rates

If you go through the [setup](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy) process after you've configured your account, you can set up target rate sensors. These sensors calculate the lowest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active. These sensors can then be used in automations to turn on/off devices that save you (and the planet) energy and money.

Each sensor will be in the form `binary_sensor.octopus_energy_target_{{TARGET_RATE_NAME}}`.

#### From and To times

If you're wanting your devices to come on during a certain period, for example while you're at work, you can set the minimum and/or maximum times for your target rate sensor. These are specified in 24 hour clock format and will attempt to find the optimum discovered period during these times.

If not specified, these default from `00:00:00` to `23:59:59`. However you can use this feature to change this evaluation period. 

If for example you want to look at prices overnight you could set your from time to something like `20:00` and your `to` time to something like `05:00`. If you're wanting to "shift" the evaluation period to be in line with something (e.g. agile pricing), you could set your `from` and `to` to something like `16:00`.

See the examples below for how this might work.

#### Offset

You may want your target rate sensors to turn on a period of time before the optimum discovered period. For example, you may be turning on a robot vacuum cleaner for a 30 minute clean and want it to charge during the optimum period. For this, you'd use the `offset` field and set it to `-00:30:00`, which can be both positive and negative and go up to a maximum of 24 hours.

#### Rolling Target

Depending on how you're going to use the sensor, you might want the best period to be found throughout the day so it's always applicable. For example, you might be using the sensor to turn on a washing machine which you might want to come on at the best time regardless of when you use the washing machine.

However, you might also only want the target time to occur once a day so once the best time for that day has passed it won't turn on again. For example, you might be using the sensor to turn on something that isn't time critical and could wait till the next day like a charger.

This feature is toggled on by the `Re-evaluate multiple times a day` checkbox.

#### Examples

Lets look at a few examples. Lets say we have the the following (unrealistic) set of rates

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

##### Continuous

If we look at a continuous sensor that we want on for 1 hour.

If we set no from/to times, then our 24 hour period being looked at ranges from `00:00:00` to `23:59:59`.

The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T00:00` - `2023-01-01T01:00` | `false`                            | while 5 is our lowest rate within the current 24 hour period, it doesn't cover our whole 1 hour and is next to a high 34 rate. A rate of 6 is the next available rate with a low following rate. |
| `2023-01-01T01:00` | `2023-01-02T00:00` - `2023-01-02T01:00` | `false`                            | Our lowest period is in the past, so we have to wait until our target period has passed to look at the next evaluation period. |
| `2023-01-01T01:00` | `2023-01-01T04:30` - `2023-01-01T05:30` | `true`                             | The rate of 6 is in the past, so 7 is our next lowest rate. 12 is smaller rate than 20 so we start in the rate period before to fill our desired hour. |
| `2023-01-01T23:30` | None | `true`                             | There is no longer enough time available in the current 24 hour period, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times for `05:00` to `19:00`, we then limit the period that we look at. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T05:00` - `2023-01-01T06:00` | `false`                            | The rate of 12 is no longer available as it's outside of our `from` time. |
| `2023-01-01T06:30` | `2023-01-02T05:00` - `2023-01-02T06:00` | `false`                            | Our lowest period is in the past, so we have to wait until our target period has passed to look at the next evaluation period. |
| `2023-01-01T06:30` | `2023-01-01T06:30` - `2023-01-01T07:30` | `true`                             | The rate of 7 is in the past, so we must look for the next lowest combined rate |
| `2023-01-01T18:00` | `2023-01-01T18:00` - `2023-01-01T19:00` | `true`                             | The rate of 20 is in the past, so we must look for the next lowest combined rate which is 34 |
| `2023-01-01T18:30` | None | `true`                            | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times to look over two days, from `20:00` to `06:00`, we then limit the period that we look at to overnight. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T20:00` | `2023-01-01T23:30` - `2023-01-02T01:30` | `false`                            | Our lowest rate of 5 now falls between our overnight time period so is available |
| `2023-01-02T02:00` | `2023-01-01T23:30` - `2023-01-02T01:30` | `false`                            | Our lowest period is in the past, so we have to wait until our target period has passed to look at the next evaluation period. |
| `2023-01-02T02:00` | `2023-01-02T04:30` - `2023-01-02T05:30` | `true`                             | The rate of 5 is in the past, so we must look for the next lowest combined rate, which includes our half hour rate at 7 |
| `2023-01-02T05:30` | None | `true`                             | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set an offset of `-00:30:00`, then while the times might be the same, the target rate sensor will turn on 30 minutes before the select rate period starts. Any set time restrictions **will** include the offset.

##### Intermittent

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
| `2023-01-01T06:30` | `2023-01-01T06:30` - `2023-01-01T07:00`, `2023-01-01T07:00` - `2023-01-01T07:30` | `true`                             | Both of our cheapest rates in the target range are in the past, so we must look for the next lowest combined rate |
| `2023-01-01T18:30` | None | `true`                            | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set our from/to times to look over two days, from `20:00` to `06:00`, we then limit the period that we look at to overnight. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T20:00` | `2023-01-01T23:30` - `2023-01-02T00:30`, `2023-01-02T05:00` - `2023-01-02T05:30` | `false`                            | Our lowest rate of 5 now falls between our overnight time period so is available |
| `2023-01-02T02:00` | `2023-01-01T23:30` - `2023-01-02T00:30`, `2023-01-02T05:00` - `2023-01-02T05:30` | `false`                            | Our lowest period is in the past, but we still have a rate in the future so our sensor will only come on once. |
| `2023-01-02T02:00` | `2023-01-02T02:00` - `2023-01-02T02:30`, `2023-01-02T05:00` - `2023-01-02T05:30` | `true`                             | The rate of 5 is in the past, so we must look for the next lowest combined rate, which includes our half hour rate at 7 |
| `2023-01-02T05:30` | None | `true`                             | There is no longer enough time available within our restricted time, so we have to wait until our target period has passed to look at the next evaluation period. |

If we set an offset of `-00:30:00`, then while the times might be the same, the target rate sensor will turn on 30 minutes before the select rate period starts. Any set time restrictions **will** include the offset.

### Gas Meters

When you sign into your account, if you have gas meters, we'll setup some sensors for you. They are available in m3 and kwh, where one will be estimated from the native value.

## Services

### Service octopus_energy.update_target_config

Service for updating a given target rate's config. This allows you to change target rates sensors dynamically based on other outside criteria (e.g. you need to adjust the target hours to top up home batteries).

> Please note this is temporary and will not persist between restarts.

| Attribute                | Optional | Description                                                                                                           |
| ------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `target.entity_id`       | `no`     | The name of the target sensor whose configuration is to be updated                                                    |
| `data.target_hours`      | `yes`    | The optional number of hours the target rate sensor should come on during a 24 hour period. Must be divisible by 0.5. |
| `data.target_start_time` | `yes`    | The optional time the evaluation period should start. Must be in the format of `HH:MM`.                               |
| `data.target_end_time`   | `yes`    | The optional time the evaluation period should end. Must be in the format of `HH:MM`.                                 |
| `data.target_offset`     | `yes`    | The optional offset to apply to the target rate when it starts. Must be in the format `(+/-)HH:MM:SS`                 |

This can be used via automations in the following way. Assuming we have the following inputs.

```yaml
input_number:
  octopus_energy_target_hours:
    name: Octopus Energy Target Hours
    min: 0
    max: 24

input_text:
  # From/to would ideally use input_datetime, but we need the time in a different format
  octopus_energy_target_from:
    name: Octopus Energy Target From
    initial: "00:00"
  octopus_energy_target_to:
    name: Octopus Energy Target To
    initial: "00:00"
  octopus_energy_target_offset:
    name: Octopus Energy Target Offset
    initial: "-00:00:00"
```

Then an automation might look like the following

```yaml
automations:
  - alias: Update target rate config
    trigger:
    - platform: state
      entity_id:
      - input_number.octopus_energy_target_hours
      - input_text.octopus_energy_target_from
      - input_text.octopus_energy_target_to
      - input_text.octopus_energy_target_offset
    condition: []
    action:
    - service: octopus_energy.update_target_config
      data:
        target_hours: >
          "{{ states('input_number.octopus_energy_target_hours') | string }}"
        target_start_time: >
          {{ states('input_text.octopus_energy_target_from') }}
        target_end_time: >
          {{ states('input_text.octopus_energy_target_to') }}
        target_offset: >
          {{ states('input_text.octopus_energy_target_offset') }}
      target:
        entity_id: binary_sensor.octopus_energy_target_example
```

## UI

### Upcoming Prices

If you're wanting to display upcoming prices in a nice readable format, then I'll direct you to the plugin developed by @lozzd available at https://github.com/lozzd/octopus-energy-rates-card.

## Increase Home Assistant logs

If you are having issues, it would be helpful to include Home Assistant logs as part of any raised issues. This can be done by setting the following values in your `configuration.yaml` file.

```yaml
logger:
  logs:
    custom_components.octopus_energy: debug
```

If you don't have access to this file, then you should be able to set the log levels using the [available services](https://www.home-assistant.io/integrations/logger/).

Once done, you'll need to reload the integration and then check the "Full Home Assistant Log" from the `logs page`. You should then see entries associated with this component. These entries should be provided with any raised issues. Please remove an sensitive information before posting.

## FAQ

### Data in my Home Assistant energy dashboard reported by Octopus Home Mini differs to Octopus Energy dashboard. Why is this?

The data can differ for a number of reasons.

If you are looking at the current day, then Home Assistant only updates the energy dashboard data once an hour, near the hour. This means you might be "missing" data in the energy dashboard when compared to the app. The integration also makes best effort to retrieve the data every minute, however it has been noticed that the API can fail at times to retrieve the data.

If you are comparing data in the energy dashboard to previous days data in the Octopus Energy dashboard, then this can also differ. This is because Octopus Energy favour data reported by your smart meter, as this is what your bills use, over your Home Mini.

### Can I add the sensors to the Energy dashboard?

#### I have an Octopus Home Mini

You can add the `current consumption` sensor as normal. You can then add the `current rate` sensor as `Use an entity with current price`.

#### I don't have an Octopus Home Mini

While you can add the `previous consumption` sensors to the dashboard, they will be associated with the wrong day. This is because the Energy dashboard uses the timestamp of when the sensor updates to determine which day the data should belong to. There is currently no official way of adding historic data to the dashboard.

However if you still want to add them, then you can add the `previous consumption` sensor as normal. You can then add the `previous consumption cost` sensor as `Use an entity tracking the total costs`.

### Why is my gas sensor reporting m3 when Octopus Energy reports it as kWh?

The sensor was setup when Home Assistant only supported gas sensors in m3 format. While this has been changed since, the reporting of the sensor can't be changed because this would be a breaking change for existing users. However a `kwh` sensor has been added to provide this data.

### I have sensors that are missing

The integration only looks at the first property associated with your account that doesn't have a moved out date attached to it. If you are still missing sensors, follow the instructions to increase the logs (see above).

You should then see entries associated with this component stating either sensors were added, skipped or no sensors were available at all.

The identifiers of the sensors should then be checked against your Octopus Energy dashboard to verify the correct sensors are being picked up. If this is producing unexpected results, then you should raise an issue.

### My gas consumption/costs seem out

This is most likely due to the default caloric value not matching your region/bill. This can be configured when setting up or updating your account.