# Home Assistant Octopus Energy

** WARNING: This component is currently a work in progress **

Custom component built from the ground up to bring your Octopus Energy details into Home Assistant to help you towards a more energy efficient (and or cheaper) home.

## How to install

You should take the latest [release](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/releases), and not clone the repo.

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation.

## How to setup

Setup is done entirely via the [integration UI](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy).

### Your account

When you setup your account, you will get a few sensors. 

You'll get the following sensors for each electricity meter with an active agreement:

* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MRAN_NUMBER}}_current_rate` - The rate of the current 30 minute period that energy consumption is charged at (including VAT).
* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MRAN_NUMBER}}_previous_rate` - The rate of the previous 30 minute period that energy consumption was charged at (including VAT).
* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MRAN_NUMBER}}_previous_accumulative_consumption` - The total consumption reported by the meter for the previous day.
* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MRAN_NUMBER}}_previous_accumulative_cost` - The total cost for the previous day, including the standing charge.

You'll get the following sensors if you have a gas meter with an active agreement:

* `sensor.octopus_energy_gas_current_rate` - The rate of the current day that gas consumption is charged at (including VAT).

You'll get the following sensors for each gas meter with an active agreement:

* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_previous_accumulative_consumption` - The total consumption reported by the meter for the previous day.
* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_previous_accumulative_cost` - The total cost for the previous day, including the standing charge.

While you can add these sensors to [energy dashboard](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/), because Octopus doesn't provide live consumption data, it will be off by a day.

Please note, that it's not possible to include current consumption sensors. This is due to Octopus Energy only providing data up to the previous day.

### Target Rates

If you go through the [setup](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy) process after you've configured your account, you can set up target rate sensors. These sensors calculate the lowest continuous or intermittent prices and turn on when these periods are active. These sensors can then be used in automations to turn on/off devices that save you (and the planet) energy and money.

Each sensor will be in the form `binary_sensor.octopus_energy_target_{{TARGET_RATE_NAME}}`.

### Gas Meters

When you sign into your account, if you have gas meters, we'll setup some sensors for you. However, the way these sensors report data isn't consistent between versions of the meters, and Octopus Energy doesn't expose what type of meter you have. Therefore, you have to toggle the checkbox when setting up your initial account within HA. If you've already setup your account, you can update this via the `Configure` option within the integrations configuration. This is a global setting, and therefore will apply to **all** gas meters.

## Known Issues/Limitations

- Octopus Energy only provide data up to the previous day, so it's not possible to expose current consumption. If you would like this to change, then you'll need to email Octopus Energy.
- Only the first property associated with an account that hasn't been moved out of is exposed.
- Gas meter SMETS1/SMETS2 setting has to be set globally and manually as Octopus Energy doesn't provide this information.