# FAQ

- [FAQ](#faq)
  - [Data in my Home Assistant energy dashboard reported by Octopus Home Mini differs to Octopus Energy dashboard. Why is this?](#data-in-my-home-assistant-energy-dashboard-reported-by-octopus-home-mini-differs-to-octopus-energy-dashboard-why-is-this)
  - [Can I add the sensors to the Energy dashboard?](#can-i-add-the-sensors-to-the-energy-dashboard)
  - [Why is my gas sensor reporting m3 when Octopus Energy reports it as kWh?](#why-is-my-gas-sensor-reporting-m3-when-octopus-energy-reports-it-as-kwh)
  - [I have sensors that are missing](#i-have-sensors-that-are-missing)
  - [My gas consumption/costs seem out](#my-gas-consumptioncosts-seem-out)
  - [I've been asked for my meter information in a bug request, how do I obtain this?](#ive-been-asked-for-my-meter-information-in-a-bug-request-how-do-i-obtain-this)
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

## My gas consumption/costs seem out

This is most likely due to the default caloric value not matching your region/bill. This can be configured when setting up or updating your account.

## I've been asked for my meter information in a bug request, how do I obtain this?

If you've been asked for meter information, don't worry we won't ask for anything sensitive. To obtain this information

1. Navigate to [your devices](https://my.home-assistant.io/redirect/devices/)
2. Search for "Octopus Energy"
3. Click on one of the meters
4. Click on "Download diagnostics"
5. Take the contents of the downloads json file and paste into the bug report. Remember to surround the contents with ``` both at the start and end.

## How do I increase the logs for the integration?

If you are having issues, it would be helpful to include Home Assistant logs as part of any raised issues. This can be done by setting the following values in your `configuration.yaml` file.

```yaml
logger:
  logs:
    custom_components.octopus_energy: debug
```

If you don't have access to this file, then you should be able to set the log levels using the [available services](https://www.home-assistant.io/integrations/logger/).

Once done, you'll need to reload the integration and then check the "Full Home Assistant Log" from the `logs page`. You should then see entries associated with this component. These entries should be provided with any raised issues. Please remove an sensitive information before posting.