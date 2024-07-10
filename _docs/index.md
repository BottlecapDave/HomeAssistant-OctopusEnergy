# Home Assistant Octopus Energy

## Features

Below are the main features of the integration

* [Electricity](./entities/electricity.md) and [gas](./entities/gas.md) meter support including consumption data and rate information
* [Custom sensor support to target cheapest rates](./setup/target_rate.md)
* [Custom sensor support for tracking costs of other entities](./setup/cost_tracker.md)
* [Custom sensor support for comparing to other tariffs](./setup/tariff_comparison.md)
* [Octopus Home mini support](./setup/account.md#home-mini)
* [Intelligent tariff settings support](./entities/intelligent.md)
* [Saving sessions support](./entities/octoplus.md#saving-sessions)
* [Wheel of fortune support](./entities/wheel_of_fortune.md)
* [Greener days support](./entities/greenness_forecast.md)

## How to install

There are multiple ways of installing the integration. Once you've installed the integration, you'll need to [setup your account](#how-to-setup) before you can use the integration.

### HACS

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

This integration can be installed directly via HACS. To install:

* [Add the repository](https://my.home-assistant.io/redirect/hacs_repository/?owner=BottlecapDave&repository=homeassistant-octopusenergy&category=integration) to your HACS installation
* Click `Download`

### Manual

You should take the latest [published release](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/releases). The current state of `develop` will be in flux and therefore possibly subject to change.

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation. Once installed, don't forget to restart your home assistant instance for the integration to be picked up.

## How to setup

Please follow the [setup guide](./setup/account.md) to setup your initial account. This guide details the configuration, along with the entities that will be available to you.

## Entities

### Electricity Entities

[Full list of electricity entities](./entities/electricity.md).

### Gas Entities

[Full list of gas entities](./entities/gas.md).

### Home Mini

If you are lucky enough to own an [Octopus Home Mini](https://octopus.energy/blog/octopus-home-mini/), you can now receive this data within Home Assistant. When setting up (or editing) your account within Home Assistant, you will need to check the box next to `I have a Home Mini`. This will gain the following entities which can be added to the [energy dashboard](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/):

!!! info

    You will only have the same data exposed in the integration that is available within the Octopus app. There has been reports of gas not appearing within the Octopus app (and integration) straight away, so you might have to wait a few days for this to appear. Once it's available within the Octopus app, if you reload the integration (or restart Home Assistant) then the entities should become available.

!!! warning

    Export sensors are not provided as the data is not available.

See [electricity entities](./entities/electricity.md#home-mini-entities) and [gas entities](./entities/gas.md#home-mini-entities) for more information.

### Intelligent

If you are on the [intelligent tariff](https://octopus.energy/smart/intelligent-octopus/), then you'll get a few additional entities when you install the integration. 

[List of intelligent entities](./entities/intelligent.md).

!!! warning
    
    If you switch to the intelligent tariff after you have installed the integration, you will need to reload the integration or restart your Home Assistant instance.

### Octoplus

To support Octopus Energy's [octoplus programme](https://octopus.energy/octoplus/). [Full list of octoplus entites](./entities/octoplus.md).

### Wheel of Fortune

To support the wheel of fortune that is awarded every month to customers. [Full list of wheel of fortune entites](./entities/wheel_of_fortune.md).

### Greenness Forecast

To support Octopus Energy's [greener days](https://octopus.energy/smart/greener-days/). [Full list of greenness forecast entites](./entities/greenness_forecast.md).

## Target Rate Sensors

These sensors calculate the lowest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active. If you are targeting an export meter, then the sensors will calculate the highest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active.

These sensors can then be used in automations to turn on/off devices that save you (and the planet) energy and money. You can go through this flow as many times as you need target rate sensors.

Please follow the [setup guide](./setup/target_rate.md).

## Cost Tracker Sensors

These sensors track the consumption of other existing sensors and provide a daily cost of those sensors.

Please follow the [setup guide](./setup/cost_tracker.md).

## Events

This integration raises several events, which can be used for various tasks like automations. For more information, please see the [events docs](./events.md).

## Services

This integration includes several services. Please review them in the [services doc](./services.md).

## Energy Dashboard

The core sensors have been designed to work with the energy dashboard. Please see the [energy dashboard guide](./setup/energy_dashboard.md) for instructions on how to set this up.

## Blueprints

A selection of [blueprints](./blueprints.md) are available to help get you up and running quickly with the integration.

## Community Contributions

A collection of community contributions can be found on the [community contributions](./community.md) page.

## FAQ

Before raising anything, please read through the [faq](./faq.md). If you have questions, then you can raise a [discussion](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/discussions). If you have found a bug or have a feature request please [raise it](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues) using the appropriate report template.

## Sponsorship

Please see the [sponsorship](./sponsorship.md) page for more information.
