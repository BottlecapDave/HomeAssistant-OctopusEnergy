# Home Assistant Octopus Energy

![installation_badge](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.octopus_energy.total) [![](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/bottlecapdave)
- [Home Assistant Octopus Energy](#home-assistant-octopus-energy)
  - [Features](#features)
  - [How to install](#how-to-install)
    - [Marketplace (Home Assistant 2026.11 and above)](#marketplace-home-assistant-202611-and-above)
    - [HACS (Home Assistant 2026.10 and below)](#hacs-home-assistant-202610-and-below)
    - [Manual](#manual)
  - [How to setup](#how-to-setup)
  - [Docs](#docs)
  - [FAQ](#faq)
  - [Sponsorship](#sponsorship)

Custom component built from the ground up to bring your Octopus Energy details into Home Assistant to help you towards a more energy efficient (and or cheaper) home. This integration is built against the API provided by Octopus Energy UK and has not been tested for any other countries. 

This integration is in no way affiliated with Octopus Energy.

If you find this useful and are planning on moving to Octopus Energy, why not use my [referral link](https://share.octopus.energy/gray-jade-372)?

## Features

Below are the main features of the integration

* [Electricity](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/entities/electricity/) and [gas](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/entities/gas/) meter support including consumption data and rate information
* [Custom sensor support for tracking costs of other entities](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/setup/cost_tracker)
* [Custom sensor support for comparing to other tariffs](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/setup/tariff_comparison)
* [Octopus Home mini support](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/setup/account/#home-mini)
* [Intelligent tariff settings support](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/entities/intelligent/)
* [Saving sessions support](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/entities/octoplus/#saving-sessions)
* [Wheel of fortune support](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/entities/wheel_of_fortune/)
* [Heat Pump support](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/entities/heat_pump)

## How to install

There are multiple ways of installing the integration. Once you've installed the integration, you'll need to [setup your account](#how-to-setup) before you can use the integration.

### Marketplace (Home Assistant 2026.11 and above)

[![Open your Home Assistant instance and open this repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=BottlecapDave&repository=homeassistant-octopusenergy&category=integration)

From Home Assistant 2026.11, HACS is built into Home Assistant as the Marketplace, found under `Settings` > `Marketplace`. This integration is available in the Marketplace catalog. To install:

* [Open the integration](https://my.home-assistant.io/redirect/marketplace_repository/?owner=BottlecapDave&repository=homeassistant-octopusenergy&category=integration) in the Marketplace, or search for `Octopus Energy` under `Settings` > `Marketplace`
* If this is your first time using the Marketplace, read the notice and accept it
* Click `Install`, which takes you straight into the [account setup](#how-to-setup)

If you previously installed the integration via HACS, Home Assistant moves it into the Marketplace automatically when you upgrade to 2026.11, so you don't need to reinstall.

### HACS (Home Assistant 2026.10 and below)

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

If you're on a version of Home Assistant before 2026.11, this integration can be installed directly via HACS. To install:

* [Add the repository](https://my.home-assistant.io/redirect/hacs_repository/?owner=BottlecapDave&repository=homeassistant-octopusenergy&category=integration) to your HACS installation
* Click `Download`
* Restart Home Assistant

### Manual

You should take the latest [published release](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/releases). The current state of `develop` will be in flux and therefore possibly subject to change.

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation. Once installed, don't forget to restart your home assistant instance for the integration to be picked up.

For convenience you can use this script on Linux to install or update if you are running Home Assistant in Docker or have Home Assistant OS without HACS.
```bash
#!/bin/bash
# To update / install : If updating remove integration from HA before running script to be safe
cd config || exit
(
    rm -rf custom_components/octopus_energy # Remove any existing install
    cd custom_components || exit
    curl -s https://api.github.com/repos/BottlecapDave/HomeAssistant-OctopusEnergy/releases/latest \
        | grep "zipball_url" \
        | cut -d : -f 2,3 \
        | tr -d \" \
        | tr -d , \
        | wget -O /tmp/octopus_energy.zip -qi -
    unzip /tmp/octopus_energy.zip */custom_components/octopus_energy/* -d /tmp/octo >& /dev/null
    cp -r /tmp/octo/BottlecapDave-HomeAssistant-OctopusEnergy-*/custom_components/octopus_energy/ .
    rm /tmp/octopus_energy.zip
    rm -rf /tmp/octo
)
```

## How to setup

Please follow the [setup guide](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/setup/account) to setup your initial account. This guide details the configuration, along with the sensors that will be available to you.

## Docs

To get full use of the integration, please visit the [docs](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/).

## FAQ

Before raising anything, please read through the [faq](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/faq). If you have questions, then you can raise a [discussion](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/discussions). If you have found a bug or have a feature request please [raise it](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues) using the appropriate report template.

## Sponsorship

If you are enjoying the integration, why not use my [referral link](https://share.octopus.energy/gray-jade-372) if you're not already a part of Octopus Energy, or if possible, make a one off or monthly [GitHub sponsorship](https://github.com/sponsors/bottlecapdave).
