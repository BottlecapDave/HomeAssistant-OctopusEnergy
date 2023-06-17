# Setup Account

- [Setup Account](#setup-account)
  - [Electricity Sensors](#electricity-sensors)
  - [Gas Sensors](#gas-sensors)
  - [Saving Sessions](#saving-sessions)
  - [Home Mini](#home-mini)
  - [Calorific Value](#calorific-value)
  - [Government Pricing Caps](#government-pricing-caps)


Setup is done entirely via the [integration UI](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy).

When you setup your account, you will get a few sensors.

## Electricity Sensors

A full list of electricity sensors can be found [here](./sensors/electricity.md).

## Gas Sensors

A full list of gas sensors can be found [here](./sensors/gas.md).

## Saving Sessions

To support Octopus Energy's [saving sessions](https://octopus.energy/saving-sessions/). A full list of  sensors can be found [here](./sensors/saving_sessions.md).

## Home Mini

If you are lucky enough to own an [Octopus Home Mini](https://octopus.energy/blog/octopus-home-mini/), you can now receive this data within Home Assistant. When setting up (or editing) your account within Home Assistant, you will need to check the box next to `I have a Home Mini`. This will gain the following sensors which can be added to the [energy dashboard](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/):

> Please note, you will only have the same data exposed in the integration that is available within the app. There has been reports of gas not appearing within the app (and integration) straight away, so you might have to wait a few days for this to appear. Once it's available within the app, if you reload the integration (or restart Home Assistant) then the sensors should become available.

For electricity sensors, see [here](./sensors/electricity.md#home-mini-sensors).

For gas sensors, see [here](./sensors/gas.md#home-mini-sensors)

## Calorific Value

When calculating gas costs, a calorific value is included in the calculation. Unfortunately this changes from region to region and is not provided by the Octopus Energy API. The default value of this is `40`, but if you check your latest bill you should be able to find the value for you. This will give you a more accurate consumption and cost calculation when your meter reports in `m3`.

## Government Pricing Caps

There has been inconsistencies across tariffs on whether government pricing caps are included or not. Therefore the ability to configure pricing caps has been added within you account. Please note that while rates are reflected straight away, consumption based sensors may take up to 24 hours to reflect. This is due to how they look at data and cannot be changed.