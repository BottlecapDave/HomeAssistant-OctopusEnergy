# FAQ

- [FAQ](#faq)
  - [Data in my Home Assistant energy dashboard reported by Octopus Home Mini differs to Octopus Energy dashboard. Why is this?](#data-in-my-home-assistant-energy-dashboard-reported-by-octopus-home-mini-differs-to-octopus-energy-dashboard-why-is-this)
  - [Can I add the sensors to the Energy dashboard?](#can-i-add-the-sensors-to-the-energy-dashboard)
  - [Why is my gas sensor reporting m3 when Octopus Energy reports it as kWh?](#why-is-my-gas-sensor-reporting-m3-when-octopus-energy-reports-it-as-kwh)
  - [I have sensors that are missing](#i-have-sensors-that-are-missing)
  - [I have data missing, is this an issue with the integration](#i-have-data-missing-is-this-an-issue-with-the-integration)
  - [My gas consumption/costs seem out](#my-gas-consumptioncosts-seem-out)
  - [I've been asked for my meter information in a bug request, how do I obtain this?](#ive-been-asked-for-my-meter-information-in-a-bug-request-how-do-i-obtain-this)
  - [I want to use the tariff overrides, but how do I find an available tariff?](#i-want-to-use-the-tariff-overrides-but-how-do-i-find-an-available-tariff)
  - [How do I increase the logs for the integration?](#how-do-i-increase-the-logs-for-the-integration)

## Data in my Home Assistant energy dashboard reported by Octopus Home Mini differs to Octopus Energy dashboard. Why is this?

The data can differ for a number of reasons.

If you are looking at the current day, then Home Assistant only updates the energy dashboard data once an hour, near the hour. This means you might be "missing" data in the energy dashboard when compared to the app. The integration also makes best effort to retrieve the data every minute, however it has been noticed that the API can fail at times to retrieve the data.

If you are comparing data in the energy dashboard to previous days data in the Octopus Energy dashboard, then this can also differ. This is because Octopus Energy favour data reported by your smart meter, as this is what your bills use, over your Home Mini.

## Can I add the sensors to the Energy dashboard?

See the [guide](./energy_dashboard.md) for instructions on how to add these sensors to the energy dashboard.

## Why is my gas sensor reporting m3 when Octopus Energy reports it as kWh?

The sensor was setup when Home Assistant only supported gas sensors in m3 format. While this has been changed since, the reporting of the sensor can't be changed because this would be a breaking change for existing users. However a `kwh` sensor has been added to provide this data.

## I have sensors that are missing

The integration only looks at the first property associated with your account that doesn't have a moved out date attached to it. If you are still missing sensors, follow the instructions to increase the logs (see above).

You should then see entries associated with this component stating either sensors were added, skipped or no sensors were available at all.

The identifiers of the sensors should then be checked against your Octopus Energy dashboard to verify the correct sensors are being picked up. If this is producing unexpected results, then you should raise an issue.

## I have data missing, is this an issue with the integration

Data can not appear for a variety of reasons. Before raising any issues, check if the data is available within the app. If it's not available within the app, then unfortunately there is nothing I can do. Data might also not appear if you lose internet connection of the Octopus Energy APIs report errors, which can occur from time to time. This will be indicated in your Home Assistant logs. If none of this is applicable, then please raise an issue so we can try and solve the problem.

## My gas consumption/costs seem out

This is most likely due to the default caloric value not matching your region/bill. This can be configured when setting up or updating your account.

## I've been asked for my meter information in a bug request, how do I obtain this?

If you've been asked for meter information, don't worry we won't ask for anything sensitive. To obtain this information

1. Navigate to [your devices](https://my.home-assistant.io/redirect/devices/)
2. Search for "Octopus Energy"
3. Click on one of the meters
4. Click on "Download diagnostics"
5. Take the contents of the downloads json file and paste into the bug report. Remember to surround the contents with ``` both at the start and end.

## I want to use the tariff overrides, but how do I find an available tariff?

To find an available tariff, you can use the Octopus Energy API to search for [current products](https://developer.octopus.energy/docs/api/#list-products). Once a product has been found, you can look up the product to find the tariff in your region and for your target energy supply.

For example if I was on the tariff `E-1R-SUPER-GREEN-24M-21-07-30-A` and I wanted to check `Flexible Octopus November 2022 v1`. I would look up all of the [products](https://api.octopus.energy/v1/products) and look for my target under `full_name` or `display_name`. I would then look up the product by taking the specified `code` and putting it at the end of the [products url](https://api.octopus.energy/v1/products). 

![All products example](./assets/product_lookup.png)

In this scenario, the `code` is `VAR-22-11-01` and so the product url is [https://api.octopus.energy/v1/products/VAR-22-11-01](https://api.octopus.energy/v1/products/VAR-22-11-01). From this list, I would then look up the tariff for my region (e.g. `A` defined at the end of my current tariff) which is defined in the `code` field. It is this value that you add to the `cost_override_tariff` sensors. In this example, I want the duel electricity tariff version, so will pick `E-2R-VAR-22-11-01-A`.

![Target product example](./assets/product_tariff_lookup.png)

## How do I increase the logs for the integration?

If you are having issues, it would be helpful to include Home Assistant logs as part of any raised issue. This can be done by following the [instructions](https://www.home-assistant.io/docs/configuration/troubleshooting/#enabling-debug-logging) outlined by Home Assistant.

You should run these logs for about a day and then include the contents in the issue. Please be sure to remove any personal identifiable information from the logs before including them.