# Home Assistant Octopus Energy

Custom component to bring your Octopus Energy details into Home Assistant to help you towards a more energy efficient (and or cheaper) home.

## How to install

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation.

## How to setup

Setup is done entirely via the [UI](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy).

When you setup your account, you will get the following sensors:

* Current Electricity Rate
* Current Electricity Consumption (if electricity details are supplied)
* Current Gas Consumption (if gas details are supplied)

You can use the consumption sensors as part of your [energy dashboard](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/).