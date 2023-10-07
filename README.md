# Home Assistant Octopus Energy

![installation_badge](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.octopus_energy.total) [![](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/bottlecapdave)
- [Home Assistant Octopus Energy](#home-assistant-octopus-energy)
  - [How to install](#how-to-install)
    - [HACS](#hacs)
    - [Manual](#manual)
  - [How to setup](#how-to-setup)
  - [Target Rate Sensors](#target-rate-sensors)
  - [Events](#events)
  - [Energy Dashboard](#energy-dashboard)
  - [Community Contributions](#community-contributions)
  - [FAQ](#faq)
  - [Sponsorship](#sponsorship)

Custom component built from the ground up to bring your Octopus Energy details into Home Assistant to help you towards a more energy efficient (and or cheaper) home. This integration is built against the API provided by Octopus Energy UK and has not been tested for any other countries. 

This integration is in no way affiliated with Octopus Energy.

If you find this useful and are planning on moving to Octopus Energy, why not use my [referral link](https://share.octopus.energy/gray-jade-372)?

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

Please follow the [setup guide](./_docs/setup_account.md) to setup your initial account. This guide details the configuration, along with the sensors that will be available to you.

## Target Rate Sensors

These sensors calculate the lowest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active. If you are targeting an export meter, then the sensors will calculate the highest continuous or intermittent rates **within a 24 hour period** and turn on when these periods are active.

These sensors can then be used in automations to turn on/off devices that save you (and the planet) energy and money. You can go through this flow as many times as you need target rate sensors.

Please follow the [setup guide](./_docs/setup_target_rate.md) to setup.

## Events

This integration raises several events, which can be used for various tasks like automations. For more information, please see the [events docs](./_docs/events.md).

## Energy Dashboard

The core sensors have been designed to work with the energy dashboard. Please see the [guide](./_docs/energy_dashboard.md) for instructions on how to set this up.

## Community Contributions

A collection of community contributions can be found [here](./_docs/community.md).

## FAQ

Before raising anything, please read through the [faq](./_docs/faq.md). If you have questions, then you can raise a [discussion](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/discussions). If you have found a bug or have a feature request please [raise it](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues) using the appropriate report template.

## Sponsorship

If you are enjoying the integration, why not use my [referral link](https://share.octopus.energy/gray-jade-372) if you're not already a part of Octopus Energy, or if possible, make a one off or monthly [GitHub sponsorship](https://github.com/sponsors/bottlecapdave).