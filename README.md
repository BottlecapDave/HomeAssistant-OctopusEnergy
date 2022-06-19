# Home Assistant Octopus Energy

** WARNING: This component is currently a work in progress **

Custom component built from the ground up to bring your Octopus Energy details into Home Assistant to help you towards a more energy efficient (and or cheaper) home.

## How to install

You should take the latest published [release](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/releases). The current state of `develop` will be in flux and therefore possibly subject to change.

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation.

### HACS

While the integration isn't available in the HACS store yet, you can install it as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories), providing the url `https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy` and category of `integration`.

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

* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption` - The total consumption reported by the meter for the previous day.
* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_cost` - The total cost for the previous day, including the standing charge.

While you can add these sensors to [energy dashboard](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/), because Octopus doesn't provide live consumption data, it will be off by a day.

Please note, that it's not possible to include current consumption sensors. This is due to Octopus Energy only providing data up to the previous day.

### Target Rates

If you go through the [setup](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy) process after you've configured your account, you can set up target rate sensors. These sensors calculate the lowest continuous or intermittent rates and turn on when these periods are active. These sensors can then be used in automations to turn on/off devices that save you (and the planet) energy and money.

Each sensor will be in the form `binary_sensor.octopus_energy_target_{{TARGET_RATE_NAME}}`.

#### Minimum and Maximum times

If you're wanting your devices to come on during a certain period, for example while you're at work, you can set the minimum and/or maximum times for your target rate sensor. These are specified in 24 hour clock format and will attempt to find the optimum discovered period during these times.

#### Offset

You may want your target rate sensors to turn on a period of time before the optimum discovered period. For example, you may be turning on a robot vacuum cleaner for a 30 minute clean and want it to charge during the optimum period. For this, you'd use the `offset` field and set it to `-00:30:00`, which can be both positive and negative and go up to a maximum of 24 hours.

### Gas Meters

When you sign into your account, if you have gas meters, we'll setup some sensors for you. However, the way these sensors report data isn't consistent between versions of the meters, and Octopus Energy doesn't expose what type of meter you have. Therefore, you have to toggle the checkbox when setting up your initial account within HA. If you've already setup your account, you can update this via the `Configure` option within the integrations configuration. This is a global setting, and therefore will apply to **all** gas meters.

## FAQ

### I have sensors that are missing

The integration only looks at the first property associated with your account that doesn't have a moved out date attached to it. If you are still missing sensors,  the first thing to do is increase the log levels for the component. This can be done by setting the following values in your `configuration.yaml` file.

```yaml
logger:
  logs:
    custom_components.octopus_energy: debug
```

If you don't have access to this file, then you should be able to set the log levels using the [available services](https://www.home-assistant.io/integrations/logger/).

Once done, you'll need to reload the integration and then check the "Full Home Assistant Log" from the `logs page`. You should then see entries associated with this component stating either sensors were added, skipped or no sensors were available at all. 

The identifiers of the sensors should then be checked against your Octopus Energy dashboard to verify the correct sensors are being picked up. If this is producing unexpected results, then you should raise an issue.

### Can I get live sensor data?

Unfortunately, Octopus Energy only provide data up to the previous day, so it's not possible to expose current consumption. If you would like this to change, then you'll need to email Octopus Energy.

### Can I add the sensors to the Energy dashboard?

While you can add the sensors to the dashboard, they will be associated with the wrong day. This is because the Energy dashboard uses the timestamp of when the sensor updates to determine which day the data should belong to. There is currently no official way of adding historic data to the dashboard, however there are indications this may be coming.

### My gas sensor consumption readings don't look quite right

This may be due to the integration being configured against the wrong kind of gas sensor. The gas meter SMETS1/SMETS2 setting has to be set globally and manually as Octopus Energy doesn't provide this information with their API. When this is set, we then know how to interpret the provided data.