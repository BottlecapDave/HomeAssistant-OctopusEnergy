# Account

Setup is done entirely via the [integration UI](https://my.home-assistant.io/redirect/config_flow_start/?domain=octopus_energy).

## Home Mini

If you are lucky enough to own an [Octopus Home Mini](https://octopus.energy/blog/octopus-home-mini/), you can now receive this data within Home Assistant. When setting up (or editing) your account within Home Assistant, you will need to check the box next to `I have a Home Mini`. This will gain the following entities which can be added to the [energy dashboard](https://www.home-assistant.io/blog/2021/08/04/home-energy-management/):

!!! info

    You will only have the same data exposed in the integration that is available within the app. There has been reports of gas not appearing within the app (and integration) straight away, so you might have to wait a few days for this to appear. Once it's available within the app, if you reload the integration (or restart Home Assistant) then the entities should become available.

!!! warning

    Export sensors are not provided as the data is not available

See [electricity entities](../entities/electricity.md#home-mini-entities) and [gas entities](../entities/gas.md#home-mini-entities) for more information.

### Refresh Rate In Minutes

This determines how often data related to your Home Mini is retrieved from Octopus Energy. The Octopus Energy APIs have a rate limit of 100 calls per hour, which is shared among all calls including through the app. The defaults are usually enough for one electricity and one gas meter's data to be retrieved. However, if you are using other integrations, have more meters being tracked or want the app to not be effected you may want to increase this rate.

You can adjust these independently between gas and electricity.

## Previous Consumption Days Offset

By default, the previous consumptions sensors are set up to pull and record the last days worth of data, to be as up-to-date as possible via the default available data. However, some people may find that Octopus Energy are delayed in being able to retrieve data from their smart meters, typically their gas smart meters. Therefore you can adjust the number of days the previous consumption sensors pull data from. This defaults to the previous day, but increasing to `2` would look at 48 hours behind, and so on. You can adjust this independently between gas and electricity.

## Calorific Value

When calculating gas costs, a calorific value is included in the calculation. Unfortunately this changes from region to region and is not provided by the Octopus Energy API. The default value of this is `40`, but if you check your latest bill you should be able to find the value for you. This will give you a more accurate consumption and cost calculation when your meter reports in `m3`.

!!! info

    Changing this will change future calculations. It will not change calculations that have been made in the past.

## Pricing Caps

There has been inconsistencies across tariffs on whether government pricing caps are included or not. Therefore the ability to configure pricing caps has been added within you account. This is configured in pounds and pence format (e.g. 0.12 for 12p).

!!! info

    While rates are reflected straight away, consumption based sensors may take up to 24 hours to reflect. This is due to how they look at data and cannot be changed.

## Favour direct debit rates

There are some tariffs where direct debit and non direct debit rates are available. This toggle determines which rate to use in these situations.


!!! info

    It might take a couple of minutes for these changes to reflect once changed.

## Home Pro

If you are lucky enough to own an [Octopus Home Pro](https://forum.octopus.energy/t/for-the-pro-user/8453/2352/), you can now receive this data locally from within Home Assistant. 

!!! warning

    Integrating with the Octopus Home Pro is currently experimental. Use at your own risk.

### Prerequisites

The Octopus Home Pro has an internal API which is not currently exposed. In order to make this data available for consumption by this integration you will need to expose a custom API on your device by following the instructions below

1. Follow [the instructions](https://github.com/OctopusSmartEnergy/Home-Pro-SDK-Public/blob/main/Home.md#sdk) to connect to your Octopus Home Pro via SSH
2. Run the command `wget -O setup_ha.sh https://raw.githubusercontent.com/BottlecapDave/HomeAssistant-OctopusEnergy/main/home_pro_server/setup.sh` to download the installation script
3. Run the command `chmod +x setup_ha.sh` to make the script executable
4. Run the command `./setup_ha.sh` to run the installation script
5. Edit `startup.sh` and add the following **before** the line `# Start the ssh server`

```
export SERVER_AUTH_TOKEN=thisisasecrettoken # Replace with your own unique string. This can be anything you wish. 
(cd /root/bottlecapdave_homeassistant_octopus_energy && ./start_server.sh)
```

At the time of writing, your `startup.sh` should now look _something_ like the following

```
#!/bin/bash

# Ensure our main env shows up in ssh sessions
# we're passing on API host info
env | grep _ >> /etc/environment

export SERVER_AUTH_TOKEN=thisisasecrettoken # Replace with your own unique string. This can be anything you wish.
(cd /root/bottlecapdave_homeassistant_octopus_energy && ./start_server.sh)

# Start the ssh server
/usr/sbin/sshd -D
```

6. Restart your Octopus Home Pro

### Settings

Once the API has been configured, you will need to set the address to the IP address of your Octopus Home Pro followed by the port 8000 (e.g. `http://192.168.1.2:8000`) and the api key to the value you set `SERVER_AUTH_TOKEN` to.


### Entities

See [entities](../entities/home_pro.md) for more information.