# Home Assistant Octopus Energy

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

## Target Rate Sensors

These sensors calculate the lowest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active. If you are targeting an export meter, then the sensors will calculate the highest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active.

These sensors can then be used in automations to turn on/off devices that save you (and the planet) energy and money. You can go through this flow as many times as you need target rate sensors.

Please follow the [setup guide](./setup/target_rate.md).

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
