# Setup Account

- [Setup Account](#setup-account)
  - [Home Mini](#home-mini)
    - [Refresh Rate In Minutes](#refresh-rate-in-minutes)
  - [Previous Consumption Days Offset](#previous-consumption-days-offset)
  - [Calorific Value](#calorific-value)
  - [Pricing Caps](#pricing-caps)


Setup is done entirely via the [integration UI](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy).

## Home Mini

If you are lucky enough to own an [Octopus Home Mini](https://octopus.energy/blog/octopus-home-mini/), you can now receive this data within Home Assistant. When setting up (or editing) your account within Home Assistant, you will need to check the box next to `I have a Home Mini`. This will gain the following entities which can be added to the [energy dashboard](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/):

> Please note, you will only have the same data exposed in the integration that is available within the app. There has been reports of gas not appearing within the app (and integration) straight away, so you might have to wait a few days for this to appear. Once it's available within the app, if you reload the integration (or restart Home Assistant) then the entities should become available.

See [electricity entities](./entities/electricity.md#home-mini-entities) and [gas entities](./entities/gas.md#home-mini-entities) for more information.

### Refresh Rate In Minutes

This determines how often data related to your Home Mini is retrieved from Octopus Energy. The Octopus Energy APIs have a rate limit of 100 calls per hour, which is shared among all calls including through the app. This is usually enough for one meter's data to be retrieved once a minute. However, if you are using other integrations, have more than one meter (e.g. gas) or want the app to not be effected you may want to increase this rate. 

You can adjust these independently between gas and electricity.

## Previous Consumption Days Offset

By default, the previous consumptions sensors are set up to pull and record the last days worth of data, to be as up-to-date as possible via the default available data. However, some people may find that Octopus Energy are delayed in being able to retrieve data from their smart meters, typically their gas smart meters. Therefore you can adjust the number of days the previous consumption sensors pull data from. This defaults to the previous day, but increasing to `2` would look at 48 hours behind, and so on. You can adjust this independently between gas and electricity.

## Calorific Value

When calculating gas costs, a calorific value is included in the calculation. Unfortunately this changes from region to region and is not provided by the Octopus Energy API. The default value of this is `40`, but if you check your latest bill you should be able to find the value for you. This will give you a more accurate consumption and cost calculation when your meter reports in `m3`.

## Pricing Caps

There has been inconsistencies across tariffs on whether government pricing caps are included or not. Therefore the ability to configure pricing caps has been added within you account. Please note that while rates are reflected straight away, consumption based sensors may take up to 24 hours to reflect. This is due to how they look at data and cannot be changed.
