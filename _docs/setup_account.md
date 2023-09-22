# Setup Account

- [Setup Account](#setup-account)
  - [Electricity Sensors](#electricity-sensors)
  - [Gas Sensors](#gas-sensors)
  - [Saving Sessions](#saving-sessions)
  - [Home Mini](#home-mini)
    - [Refresh Rate In Minutes](#refresh-rate-in-minutes)
  - [Intelligent Tariff](#intelligent-tariff)
  - [Previous Consumption Days Offset](#previous-consumption-days-offset)
  - [Calorific Value](#calorific-value)
  - [Government Pricing Caps](#government-pricing-caps)
  - [Services](#services)
    - [Service octopus\_energy.purge\_invalid\_external\_statistic\_ids](#service-octopus_energypurge_invalid_external_statistic_ids)


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

### Refresh Rate In Minutes

This determines how often data related to your Home Mini is retrieved from Octopus Energy. The Octopus Energy APIs have a rate limit of 100 calls per hour, which is shared among all calls including through the app. This is usually enough for one meter's data to be retrieved once a minute. However, if you are using other integrations, have more than one meter (e.g. gas) or want the app to not be effected you may want to increase this rate. 

You can adjust these independently between gas and electricity.

## Intelligent Tariff

If you are on the [intelligent tariff](https://octopus.energy/smart/intelligent-octopus/), then you'll get a few additional sensors when you install the integration. 

A full list of intelligent sensors can be found [here](./sensors/intelligent.md)

> Please note: If you switch to the intelligent tariff after you have installed the integration, you will need to reload the integration or restart your Home Assistant instance.

## Previous Consumption Days Offset

By default, the previous consumptions sensors are set up to pull and record the last days worth of data, to be as up-to-date as possible via the default available data. However, some people may find that Octopus Energy are delayed in being able to retrieve data from their smart meters, typically their gas smart meters. Therefore you can adjust the number of days the previous consumption sensors pull data from. This defaults to the previous day, but increasing to `2` would look at 48 hours behind, and so on. You can adjust this independently between gas and electricity.

## Calorific Value

When calculating gas costs, a calorific value is included in the calculation. Unfortunately this changes from region to region and is not provided by the Octopus Energy API. The default value of this is `40`, but if you check your latest bill you should be able to find the value for you. This will give you a more accurate consumption and cost calculation when your meter reports in `m3`.

## Government Pricing Caps

There has been inconsistencies across tariffs on whether government pricing caps are included or not. Therefore the ability to configure pricing caps has been added within you account. Please note that while rates are reflected straight away, consumption based sensors may take up to 24 hours to reflect. This is due to how they look at data and cannot be changed.

## Services

### Service octopus_energy.purge_invalid_external_statistic_ids

Service for removing all external statistics that are associated with meters that don't have an active tariff. This is useful if you've been using the integration and obtained new smart meters.