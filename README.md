# Home Assistant Octopus Energy

- [Home Assistant Octopus Energy](#home-assistant-octopus-energy)
  - [How to install](#how-to-install)
    - [HACS](#hacs)
  - [How to setup](#how-to-setup)
    - [Your account](#your-account)
      - [Saving Sessions](#saving-sessions)
    - [Target Rates](#target-rates)
      - [From and To times](#from-and-to-times)
      - [Offset](#offset)
      - [Rolling Target](#rolling-target)
      - [Examples](#examples)
        - [Continuous](#continuous)
- [Continuous Nothing](#continuous-nothing)
- [Continuous from/to](#continuous-fromto)
- [Continuous from/to with offset](#continuous-fromto-with-offset)
- [Continuous from/to and rolling target](#continuous-fromto-and-rolling-target)
- [Continuous from/to and offset](#continuous-fromto-and-offset)
- [intermediate Nothing](#intermediate-nothing)
- [intermediate from/to](#intermediate-fromto)
- [intermediate from/to with offset](#intermediate-fromto-with-offset)
- [intermediate from/to and rolling target](#intermediate-fromto-and-rolling-target)
- [intermediate from/to and offset](#intermediate-fromto-and-offset)
    - [Gas Meters](#gas-meters)
  - [Increase Home Assistant logs](#increase-home-assistant-logs)
  - [FAQ](#faq)
    - [Can I get live sensor data? Do you support the new Octopus Home Mini?](#can-i-get-live-sensor-data-do-you-support-the-new-octopus-home-mini)
    - [Can I add the sensors to the Energy dashboard?](#can-i-add-the-sensors-to-the-energy-dashboard)
    - [Why is my gas sensor reporting m3 when Octopus Energy reports it as kWh?](#why-is-my-gas-sensor-reporting-m3-when-octopus-energy-reports-it-as-kwh)
    - [I have sensors that are missing](#i-have-sensors-that-are-missing)

Custom component built from the ground up to bring your Octopus Energy details into Home Assistant to help you towards a more energy efficient (and or cheaper) home. This integration is built against the API provided by Octopus Energy UK and has not been tested for any other divisions. This integration is in no way affiliated with Octopus Energy.

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

You'll get the following sensors if you have a gas meter with an active agreement:

* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_rate` - The rate of the current day that gas consumption is charged at (including VAT).

You'll get the following sensors for each gas meter with an active agreement:

* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption` - The total consumption reported by the meter for the previous day in m3. If your meter reports in m3, then this will be an accurate value reported by Octopus, otherwise it will be a calculated value.
* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption_kwh` - The total consumption reported by the meter for the previous day in kwh. If your meter reports in kwh, then this will be an accurate value reported by Octopus, otherwise it will be a calculated value.
* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_cost` - The total cost for the previous day, including the standing charge.

While you can add these sensors to [energy dashboard](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/), because Octopus doesn't provide live consumption data, it will be off by a day.

Please note, that it's not possible to include current consumption sensors. This is due to Octopus Energy only providing data up to the previous day.

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
| `2023-01-01T00:00` | `2023-01-01T00:00`-`2023-01-01T01:00` | `false`                            | while 5 is our lowest rate within the current 24 hour period, it doesn't cover our whole 1 hour and is next to a high 34 rate. A rate of 6 is the next available rate with a low following rate. |
| `2023-01-01T01:00` | `2023-01-02T00:00`-`2023-01-02T01:00` | `false`                            | Our lowest period is in the past, so we must look to the next day |
| `2023-01-01T01:00` | `2023-01-01T04:30`-`2023-01-01T05:30` | `true`                             | The rate of 6 is in the past, so 7 is our next lowest rate. 12 is smaller rate than 20 so we start in the rate period before to fill our desired hour. |
| `2023-01-01T23:30` | `2023-01-02T00:00`-`2023-01-02T01:00` | `true`                             | There is no longer enough time available in the current 24 hour period, so we must look to the next day. |

If we set our from/to times for `05:00` to `19:00`, we then limit the period that we look at. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T00:00` | `2023-01-01T05:00`-`2023-01-01T06:00` | `false`                            | The rate of 12 is no longer available as it's outside of our `from` time. |
| `2023-01-01T06:30` | `2023-01-02T05:00`-`2023-01-02T06:00` | `false`                            | Our lowest period is in the past, so we must look to the next day |
| `2023-01-01T06:30` | `2023-01-01T06:30`-`2023-01-01T07:30` | `true`                             | The rate of 7 is in the past, so we must look for the next lowest combined rate |
| `2023-01-01T18:00` | `2023-01-01T18:00`-`2023-01-01T19:00` | `true`                             | The rate of 20 is in the past, so we must look for the next lowest combined rate which is 34 |
| `2023-01-01T18:30` | `2023-01-02T05:00`-`2023-01-02T06:00` | `true`                            | There is no longer enough time available within our restricted time, so we must look to the next day. |

If we set our from/to times to look over two days, `06:00` to `20:00`, we then limit the period that we look at. The following table shows what this would be like.

| current date/time  | period                                | `Re-evaluate multiple times a day` | reasoning |
| ------------------ | ------------------------------------- | ---------------------------------- | --------- |
| `2023-01-01T20:00` | `2023-01-01T23:30`-`2023-01-02T01:30` | `false`                            | Our lowest rate of 5 now falls between our overnight time period so is available |
| `2023-01-02T02:00` | `2023-01-02T23:30`-`2023-01-03T01:30` | `false`                            | Our lowest period is in the past, so we must look to the next day |
| `2023-01-02T02:00` | `2023-01-02T02:00`-`2023-01-02T03:00` | `true`                             | The rate of 5 is in the past, so we must look for the next lowest combined rate |
| `2023-01-01T05:30` | `2023-01-02T23:30`-`2023-01-03T01:30` | `true`                             | There is no longer enough time available within our restricted time, so we must look to the next day. |

# Continuous Nothing
# Continuous from/to
# Continuous from/to with offset
# Continuous from/to and rolling target
# Continuous from/to and offset

# intermediate Nothing
# intermediate from/to
# intermediate from/to with offset
# intermediate from/to and rolling target
# intermediate from/to and offset

### Gas Meters

When you sign into your account, if you have gas meters, we'll setup some sensors for you. However, the way these sensors report data isn't consistent between versions of the meters, and Octopus Energy doesn't expose what type of meter you have. Therefore, you have to toggle the checkbox when setting up your initial account within HA. If you've already setup your account, you can update this via the `Configure` option within the integrations configuration. This is a global setting, and therefore will apply to **all** gas meters.

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

### Can I get live sensor data? Do you support the new Octopus Home Mini?

Unfortunately, Octopus Energy only provide data up to the previous day, so it's not possible to expose current consumption. They also haven't provided any public APIs for accessing the data provided by [Octopus Home Mini](https://octopus.energy/blog/octopus-home-mini/).

If you would like this to change, then you'll need to email Octopus Energy and raise your interests.

### Can I add the sensors to the Energy dashboard?

While you can add the sensors to the dashboard, they will be associated with the wrong day. This is because the Energy dashboard uses the timestamp of when the sensor updates to determine which day the data should belong to. There is currently no official way of adding historic data to the dashboard, however there are indications this may be coming.

### Why is my gas sensor reporting m3 when Octopus Energy reports it as kWh?

The sensor was setup when Home Assistant only supported gas sensors in m3 format. While this has been changed since, the reporting of the sensor can't be changed because this would be a breaking change for existing users.

### I have sensors that are missing

The integration only looks at the first property associated with your account that doesn't have a moved out date attached to it. If you are still missing sensors, follow the instructions to increase the logs (see above).

You should then see entries associated with this component stating either sensors were added, skipped or no sensors were available at all.

The identifiers of the sensors should then be checked against your Octopus Energy dashboard to verify the correct sensors are being picked up. If this is producing unexpected results, then you should raise an issue.