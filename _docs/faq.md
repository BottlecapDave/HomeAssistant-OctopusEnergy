# FAQ

- [FAQ](#faq)
  - [Data in my Home Assistant energy dashboard reported by Octopus Home Mini differs to Octopus Energy dashboard. Why is this?](#data-in-my-home-assistant-energy-dashboard-reported-by-octopus-home-mini-differs-to-octopus-energy-dashboard-why-is-this)
  - [I've added my previous consumption sensors to the Energy dashboard, but they are reported in a single chunk and are a day or more out. Is this a bug?](#ive-added-my-previous-consumption-sensors-to-the-energy-dashboard-but-they-are-reported-in-a-single-chunk-and-are-a-day-or-more-out-is-this-a-bug)
  - [Why are the names of the entities so long, and can you change them to be shorted?](#why-are-the-names-of-the-entities-so-long-and-can-you-change-them-to-be-shorted)
  - [I am getting warnings about entities taking too long to update. Is this normal?](#i-am-getting-warnings-about-entities-taking-too-long-to-update-is-this-normal)
  - [Why is my gas sensor reporting m3 when Octopus Energy reports it as kWh?](#why-is-my-gas-sensor-reporting-m3-when-octopus-energy-reports-it-as-kwh)
  - [There are entities that are disabled. Why are they disabled and how do I enable them?](#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them)
  - [I have entities that are missing](#i-have-entities-that-are-missing)
  - [I have data missing, is this an issue with the integration](#i-have-data-missing-is-this-an-issue-with-the-integration)
  - [I'm an agile user and having trouble setting up a target rate sensor. What am I doing wrong?](#im-an-agile-user-and-having-trouble-setting-up-a-target-rate-sensor-what-am-i-doing-wrong)
  - [Why won't my target rates update?](#why-wont-my-target-rates-update)
  - [My gas consumption/costs seem out](#my-gas-consumptioncosts-seem-out)
  - [I want to use the tariff overrides, but how do I find an available tariff?](#i-want-to-use-the-tariff-overrides-but-how-do-i-find-an-available-tariff)
  - [How do I know when there's any update available?](#how-do-i-know-when-theres-any-update-available)
  - [I've been asked for my meter information in a bug request, how do I obtain this?](#ive-been-asked-for-my-meter-information-in-a-bug-request-how-do-i-obtain-this)
  - [How do I increase the logs for the integration?](#how-do-i-increase-the-logs-for-the-integration)

## Data in my Home Assistant energy dashboard reported by Octopus Home Mini differs to Octopus Energy dashboard. Why is this?

The data can differ for a number of reasons.

If you are looking at the current day, then Home Assistant only updates the energy dashboard data once an hour, near the hour. This means you might be "missing" data in the energy dashboard when compared to the app. The integration also makes best effort to retrieve the data every minute, however it has been noticed that the API can fail at times to retrieve the data.

If you are comparing data in the energy dashboard to previous days data in the Octopus Energy dashboard, then this can also differ. This is because Octopus Energy favour data reported by your smart meter, as this is what your bills use, over your Home Mini.

## I've added my previous consumption sensors to the Energy dashboard, but they are reported in a single chunk and are a day or more out. Is this a bug?

While you can add the `previous consumption` sensors to the dashboard, they will be associated with the wrong day. This is because the Energy dashboard uses the timestamp of when the sensor updates to determine which day the data should belong to.

Instead, you can use different external statistics that are exported by the `previous consumption` sensors, which are broken down into hourly chunks. Please note it can take **up to 24 hours** for the external statistics to appear.

Please follow the [guide](./energy_dashboard.md#previous-day-consumption) for instructions on how to add these separate sensors to the energy dashboard.

You should not have this issue for current consumption sensors, as they are updated in realtime.

## Why are the names of the entities so long, and can you change them to be shorted?

The names and ids of the entities are long to avoid clashes with both other integrations and with other meters that might be associated with your account. However you are free to update the names and/or ids to something more concise for you as per the [Home Assistant docs](https://www.home-assistant.io/docs/configuration/customizing-devices/#changing-the-entity-id).

## I am getting warnings about entities taking too long to update. Is this normal?

If you receiving warnings along the lines of

> Update of sensor.octopus_energy_xxx is taking over x seconds

> Updating octopus_energy sensor took longer than the scheduled update interval

then yes, this is expected. This is a default warning built into Home Assistant, however with this integration it's perfectly valid for you to receive this when the sensors attempt to update the data. This is for a number of reasons

1. Your internet connection is slow
2. Octopus Energy APIs are slow to respond, or having issues.

If you wish to suppress this warning, you can follow [this advice](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/429#issuecomment-1783739547).

## Why is my gas sensor reporting m3 when Octopus Energy reports it as kWh?

The sensor was setup when Home Assistant only supported gas sensors in m3 format. While this has been changed since, the reporting of the sensor can't be changed because this would be a breaking change for existing users. However a `kwh` sensor has been added to provide this data.

## There are entities that are disabled. Why are they disabled and how do I enable them?

Some entities are disabled by default. This is usually because the entities are not applicable for all tariffs or are for niche scenarios. By having these entities disabled, it also doesn't overwhelm new users when they install the integration otherwise most users will be presented with over 40 different entities.

Enabling entities is easy. All you need to do is

1. Go to the [Octopus Energy](https://my.home-assistant.io/redirect/integration/?domain=octopus_energy) integration.
2. Click on `entities`
3. Find and click on the entity you want to enable. This is usually indicated by a "no entry" sign in the `status`.
4. Click on the settings/cog button
5. Click on the `enable` button or toggle the `Enabled` toggle to on
6. Click on `update`

## I have entities that are missing

The integration only looks at the first property associated with your account that doesn't have a moved out date attached to it. If you are still missing entities, follow the instructions to [increase the logs](#how-do-i-increase-the-logs-for-the-integration).

You should then see entries associated with this component stating either entities were added, skipped or no entities were available at all.

The identifiers of the entities should then be checked against your Octopus Energy dashboard to verify the correct entities are being picked up. If this is producing unexpected results, then you should raise an issue.

## I have data missing, is this an issue with the integration

Data can not appear for a variety of reasons. Before raising any issues, check if the data is available within the app. If it's not available within the app, then unfortunately there is nothing I can do. Data might also not appear if you lose internet connection or the Octopus Energy APIs report errors, which can occur from time to time. This will be indicated in your Home Assistant logs. If none of this is applicable, then please raise an issue so we can try and solve the problem.

## I'm an agile user and having trouble setting up a target rate sensor. What am I doing wrong?

Rate data for agile tariffs are not available in full for the next day, which can cause issues with target rate sensors in their default state. We prevent you from setting up target rate sensors in this form. More information around this can be found in the [target rate documentation](./setup_target_rate.md#agile-users).

## Why won't my target rates update?

The target rate sensors are set to update every minute, which includes determining if you're within a target time period and calculating future target time periods.. This can be confirmed via the `last_evaluated` attribute. 

The `target_times` will evaluate once all rates are available for the specified time period and all existing target times are in the past. When this was last evaluated can be confirmed via the `target_times_last_evaluated` attribute. For example, if you are looking for target rates between 16:00 (today) and 16:00 (tomorrow), and you only have rates up to 23:00 (today), then target times will not be evaluated until rate information is available up to 16:00 (tomorrow). This can be confirmed by reviewing the data available in your current and next day rates entities.

If there is a delay in retrieving rate information, there is chance that when it comes to evaluation, times are picked that are in the past because they were the lowest. This will result in your target rate sensor skipping a day and waiting to calculate new target times for the next scheduled time period. This can be confirmed by comparing the `target_times` and the `target_times_last_evaluated` attribute. If this happens frequently, then please adjust the target time periods of your target rate sensor to something that works for you.

If the `last_evaluated` attribute is not updating, then please raise an issue.

## My gas consumption/costs seem out

This is most likely due to the default caloric value not matching your region/bill. This can be configured when setting up or updating your account.

## I want to use the tariff overrides, but how do I find an available tariff?

To find an available tariff, you can use the Octopus Energy API to search for [current products](https://developer.octopus.energy/docs/api/#list-products). Once a product has been found, you can look up the product to find the tariff in your region and for your target energy supply.

For example if I was on the tariff `E-1R-SUPER-GREEN-24M-21-07-30-A` and I wanted to check `Flexible Octopus November 2022 v1`. I would look up all of the [products](https://api.octopus.energy/v1/products) and look for my target under `full_name` or `display_name`. I would then look up the product by taking the specified `code` and putting it at the end of the [products url](https://api.octopus.energy/v1/products). 

![All products example](./assets/product_lookup.png)

In this scenario, the `code` is `VAR-22-11-01` and so the product url is [https://api.octopus.energy/v1/products/VAR-22-11-01](https://api.octopus.energy/v1/products/VAR-22-11-01). From this list, I would then look up the tariff for my region (e.g. `A` defined at the end of my current tariff) which is defined in the `code` field. It is this value that you add to the `cost_override_tariff` entity. In this example, I want the duel electricity tariff version, so will pick `E-2R-VAR-22-11-01-A`.

![Target product example](./assets/product_tariff_lookup.png)

## How do I know when there's any update available?

If you've installed via HACS, then you can keep an eye on `sensor.hacs` to see the number of pending updates. This could be used with an automation or highlighted on your dashboard. This will include any HACS integration update, not just this one. If you're feeling a little more adventurous, then you can enable HACS' [experimental features](https://hacs.xyz/docs/configuration/options/). This will surface any available updates in the normal update location within Home Assistant.

If you've installed the integration manually, then you should keep an eye on the [GitHub releases](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/releases). You could even subscribe to the [RSS feed](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/releases.atom).

## I've been asked for my meter information in a bug request, how do I obtain this?

If you've been asked for meter information, don't worry we won't ask for anything sensitive. To obtain this information

1. Navigate to [your devices](https://my.home-assistant.io/redirect/devices/)
2. Search for "Octopus Energy"
3. Click on one of the meters
4. Click on "Download diagnostics"
5. Take the contents of the downloads json file and paste into the bug report. Remember to surround the contents with ``` both at the start and end.

## How do I increase the logs for the integration?

If you are having issues, it would be helpful to include Home Assistant logs as part of any raised issue. This can be done by following the [instructions](https://www.home-assistant.io/docs/configuration/troubleshooting/#enabling-debug-logging) outlined by Home Assistant.

You should run these logs for about a day and then include the contents in the issue. Please be sure to remove any personal identifiable information from the logs before including them.
