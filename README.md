# Home Assistant Octopus Energy

** WARNING: This component is currently a work in progress **

Custom component built from the ground up to bring your Octopus Energy details into Home Assistant to help you towards a more energy efficient (and or cheaper) home.

## How to install

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation.

Alternatively you can install as a [HACS custom repository](https://hacs.xyz/docs/faq/custom_repositories) using the URL: https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy and Category 'Integration'.

![image (1)](https://user-images.githubusercontent.com/79175134/143213247-64219170-fd42-4a1e-8d91-facb671ad4d0.png)

You then need to go to the normal Configuration Integration page and '+ Add Integration' to find Octopus Energy: 
![image (2)](https://user-images.githubusercontent.com/79175134/143213476-d9041136-ea45-41ab-9b2b-c4f23c236948.png)

From there you should be able to configure:

![image (3)](https://user-images.githubusercontent.com/79175134/143213555-1d404aa0-fa3e-4335-a49f-633f735b7fc6.png)

## How to setup

Setup is done entirely via the configuration flow [User Interface (UI)](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy).

### Your account

When you setup your account, you will get a few sensors. 

You'll get the following sensors if you have an electricity meter with an active agreement:

* `sensor.octopus_energy_electricity_current_rate` - The rate of the current 30 minute period that energy consumption is charged at (including VAT).
* `sensor.octopus_energy_electricity_previous_rate` - The rate of the previous 30 minute period that energy consumption was charged at (including VAT).

You'll get the following sensors for each electricity meter with an active agreement:

* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_latest_consumption` - The latest consumption reported by the meter. It looks like Octopus is about a day behind with their data, therefore this is often zero and will probably be removed in the future.
* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_previous_accumulative_consumption` - The total consumption reported by the meter for the previous day.

You'll get the following sensors for each gas meter with an active agreement:

* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_latest_consumption` - The latest consumption reported by the meter. It looks like Octopus is about a day behind with their data, therefore this is often zero and will probably be removed in the future.
* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_previous_accumulative_consumption` - The total consumption reported by the meter for the previous day.

While you can add these sensors to [energy dashboard](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/), because Octopus doesn't provide live consumption data, it will be off by a day.

### Target Rates

If you go through the [setup](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy) process after you've configured your account, you can set up target rate sensors. These sensors calculate the lowest continuous or intermittent prices and turn on when these periods are active. These sensors can then be used in automations to turn on/off devices that save you (and the planet) energy and money.

Each sensor will be in the form `binary_sensor.octopus_energy_target_{{TARGET_RATE_NAME}}`.

### Gas Meters

When you sign into your account, if you have gas meters, we'll setup some sensors for you. However, the way these sensors report data isn't consistent between versions of the meters, and Octopus Energy doesn't expose what type of meter you have. Therefore, you have to toggle the checkbox when setting up your initial account within HA. If you've already setup your account, you can update this via the `Configure` option within the integrations configuration. This is a global setting, and therefore will apply to **all** gas meters.

## Known Issues/Limitations

- Latest consumption is at the mercy of how often Octopus Energy updates their records. This seems to be a day behind based on local testing.
- Only the first property associated with an account is exposed.
- Gas meter SMETS1/SMETS2 setting has to be set globally and manually as Octopus Energy doesn't provide this information.
