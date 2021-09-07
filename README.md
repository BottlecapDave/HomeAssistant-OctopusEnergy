# Home Assistant Octopus Energy

** WARNING: This component is currently a work in progress **

Custom component built from the ground up to bring your Octopus Energy details into Home Assistant to help you towards a more energy efficient (and or cheaper) home.

## How to install

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation.

## How to setup

Setup is done entirely via the [UI](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy).

### Your account

When you setup your account, you will get the following sensors:

* Current Electricity Current Rate (Based on first active tariff)
* Current Electricity Previous Rate (Based on first active tariff)
* Latest Electricity Consumption (per electricity meter)
* Previous Day's Accumulative Electricity Consumption (per electricity meter)
* Latest Gas Consumption (per gas meter)
* Previous Day's Accumulative Gas Consumption (per gas meter)

Ideally, you'd be able to use the consumption sensors as part of your [energy dashboard](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/). However, while they can be added, Octopus Energy doesn't provide live consumption data.

### Target Rates

If you go through the [setup](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy) process after you've configured your account, you can set up target rate sensors. These sensors calculate the lowest continuous or intermittent points and turn on when these rates are active. These sensors can then be used in automations to turn on/off devices the save you money (and in theory be on when there's the most renewable energy).

## Known Issues/Limitations

- Latest consumption is at the mercy of how often Octopus Energy updates their records. This seems to be a day behind based on local testing.
- Only the first property associated with an account is exposed.