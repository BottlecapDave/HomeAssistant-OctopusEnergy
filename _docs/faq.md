# FAQ

## How often is data refreshed?

Based on a request from [Octopus Energy](https://forum.octopus.energy/t/pending-and-completed-octopus-intelligent-dispatches/8510/8?u=bottlecapdave), the integration polls and retrieves data at different intervals depending on the target data. Below is a rough table describing how often the integration targets refreshing various bits of data. This has been done to try and not overload the API while also providing useful data in a timely fashion - Octopus Energy estimate that ~95% of their traffic comes mainly from this integration.

| Area | Refresh rate (in minutes) | Justification |
|-|-|-|
| Account | 60 | This is mainly used to get the active meters and associated tariffs, which shouldn't change often so no need to poll often. |
| Intelligent tariff based sensors | 5 | Trying to balance refreshing settings and new dispatch information without overloading the API |
| Rate information | 15 | This is what drives most people's automations, but doesn't change that frequently. We can afford a bit of lag for API stability. |
| Current consumption data | Configurable (minimum 1) | This is most useful for a smart home to be as up-to-date as possible, but is also rate limited to 100 requests total per hour. 1 minute is enough for most people, but might need to be increased for those with multiple meters (e.g. gas and electricity) |
| Previous consumption data | 30 | This is usually refreshed once a day at various times throughout the day. We want to be up-to-date as soon as possible, without swamping the API. |
| Standing charges | 60 | This should only change if the user's tariff changes, so no need to request data too often. Keep in sync with account refreshes. |
| Saving sessions | 15 | Inactive for most of the year and new sessions have enough warning to allow a bit of lag. |
| Wheel of fortune | 60 | Doesn't change that frequently, and not fundamental for a smart home (other than knowledge) so no need to request too often. |

If data cannot be refreshed for any reason (e.g. no internet or APIs are down), then the integration will attempt to retrieve data as soon as possible, slowly waiting longer between each attempt. Below is a rough example assuming the first (failed) scheduled refresh was at `10:35`.

| Attempt | Target time |
|-|-|
| 1 | `10:35` |
| 2 | `10:36` |
| 3 | `10:38` |
| 4 | `10:41` |
| 5 | `10:45` |

Once a successful request is made, the refreshes will revert back to the redefined default intervals.

**The retrieving of data does not effect the rate the entities states/attributes are evaluated.**

## I have data missing, is this an issue with the integration?

Data can not appear for a variety of reasons. Before raising any issues, check if the data is available on the [website](https://octopus.energy/dashboard/new/accounts/consumption/home) for the requested period (e.g. for previous consumption, you'll be wanting data for the day before). If it's not available on the website, then unfortunately there is nothing that can be done and you may need to contact Octopus Energy.

Data might also not appear if you lose internet connection or the Octopus Energy APIs report errors, which can occur from time to time. This will be indicated in your Home Assistant logs as warnings around using cached data. If none of this is applicable, then please raise an issue so we can try and solve the problem.

## Data in my Home Assistant energy dashboard reported by Octopus Home Mini differs to Octopus Energy dashboard. Why is this?

The data can differ for a number of reasons.

If you are looking at the current day, then Home Assistant only updates the energy dashboard data once an hour, near the hour. This means you might be "missing" data in the energy dashboard when compared to the app. The integration also makes best effort to retrieve the data every minute, however it has been noticed that the API can fail at times to retrieve the data.

If you are comparing data in the energy dashboard to previous days data in the Octopus Energy dashboard, then this can also differ. This is because Octopus Energy favour data reported by your smart meter, as this is what your bills use, over your Home Mini.

## I've added my previous consumption sensors to the Energy dashboard, but they are reported in a single chunk and are a day or more out. Is this a bug?

While you can add the `previous consumption` sensors to the dashboard, they will be associated with the wrong day. This is because the Energy dashboard uses the timestamp of when the sensor updates to determine which day the data should belong to.

Instead, you can use different external statistics that are exported by the `previous consumption` sensors, which are broken down into hourly chunks. 

!!! info 

    It can take **up to 24 hours** for the external statistics to appear.

Please follow the [guide](./setup/energy_dashboard.md#previous-day-consumption) for instructions on how to add these separate sensors to the energy dashboard.

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

## I'm an agile user and having trouble setting up a target rate sensor. What am I doing wrong?

Rate data for agile tariffs are not available in full for the next day, which can cause issues with target rate sensors in their default state. We prevent you from setting up target rate sensors in this form. More information around this can be found in the [target rate documentation](./setup/target_rate.md#agile-users).

## Why won't my target rates update?

The target rate sensors are set to update every minute, which includes determining if you're within a target time period and calculating future target time periods.. This can be confirmed via the `last_evaluated` attribute. 

The `target_times` will evaluate once all rates are available for the specified time period and all existing target times are in the past. When this was last evaluated can be confirmed via the `target_times_last_evaluated` attribute. For example, if you are looking for target rates between 16:00 (today) and 16:00 (tomorrow), and you only have rates up to 23:00 (today), then target times will not be evaluated until rate information is available up to 16:00 (tomorrow). This can be confirmed by reviewing the data available in your current and next day rates entities.

If there is a delay in retrieving rate information, there is chance that when it comes to evaluation, times are picked that are in the past because they were the lowest. This will result in your target rate sensor skipping a day and waiting to calculate new target times for the next scheduled time period. This can be confirmed by comparing the `target_times` and the `target_times_last_evaluated` attribute. If this happens frequently, then please adjust the target time periods of your target rate sensor to something that works for you.

If the `last_evaluated` attribute is not updating, then please raise an issue.

## My gas consumption/costs seem out

Depending on the native reading from your meter or the sensor you're looking at, the consumption may have to be converted from kWh into cubic meters.

* The current consumption (m3) is always calculated, as the Home Mini provides this data in kWh via the API.
* The previous consumption sensor (m3) _may_ be calculated if your meter natively speaks in kWh. This is indicated by the `is_estimated` attribute on the sensor

Because all rates are in kWh, if any conversions are required into kWh then the cost could also be out by this conversion.

The conversion cubic meters (m3) to kWh is achieved by following this [formula](https://www.theenergyshop.com/guides/how-to-convert-gas-units-to-kwh). The part that can differ from person to person is the calorific value, which defaults in the integration to 40. This will most likely be incorrect, but unfortunately is not provided by the OE APIs. Therefore you'll need to set it as part of your [account](./setup/account.md#calorific-value). This changes throughout the year and can be found on your latest bill.

## I want to use the tariff overrides, but how do I find an available tariff?

To find an available tariff, you can use the Octopus Energy API to search for [current products](https://developer.octopus.energy/docs/api/#list-products). Once a product has been found, you can look up the product to find the tariff in your region and for your target energy supply.

For example if I was on the tariff `E-1R-SUPER-GREEN-24M-21-07-30-A` and I wanted to check `Flexible Octopus November 2022 v1`. I would look up all of the [products](https://api.octopus.energy/v1/products) and look for my target under `full_name` or `display_name`. I would then look up the product by taking the specified `code` and putting it at the end of the [products url](https://api.octopus.energy/v1/products). 

![All products example](./assets/product_lookup.png)

In this scenario, the `code` is `VAR-22-11-01` and so the product url is [https://api.octopus.energy/v1/products/VAR-22-11-01](https://api.octopus.energy/v1/products/VAR-22-11-01). From this list, I would then look up the tariff for my region (e.g. `A` defined at the end of my current tariff) which is defined in the `code` field. It is this value that you add to the `cost_override_tariff` entity. In this example, I want the duel electricity tariff version, so will pick `E-2R-VAR-22-11-01-A`.

![Target product example](./assets/product_tariff_lookup.png)

## How do I know when there's an update available?

If you've installed via HACS, then you can keep an eye on `sensor.hacs` to see the number of pending updates. This could be used with an automation or highlighted on your dashboard. This will include any HACS integration update, not just this one. If you're feeling a little more adventurous, then you can enable HACS' [experimental features](https://hacs.xyz/docs/configuration/options/). This will surface any available updates in the normal update location within Home Assistant.

If you've installed the integration manually, then you should keep an eye on the [GitHub releases](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/releases). You could even subscribe to the [RSS feed](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/releases.atom).

## How do I increase the logs for the integration?

If you are having issues, it would be helpful to include Home Assistant logs as part of any raised issue. This can be done by following the [instructions](https://www.home-assistant.io/docs/configuration/troubleshooting/#enabling-debug-logging) outlined by Home Assistant.

You should run these logs for about a day and then include the contents in the issue. Please be sure to remove any personal identifiable information from the logs before including them.

## I've been asked for my meter information in a bug request, how do I obtain this?

If you've been asked for meter information, don't worry we won't ask for anything sensitive. To obtain this information

1. Navigate to [your devices](https://my.home-assistant.io/redirect/devices/)
2. Search for "Octopus Energy"
3. Click on one of the meters
4. Click on "Download diagnostics"
5. Take the contents of the downloads json file and paste into the bug report. Remember to surround the contents with ``` both at the start and end.
