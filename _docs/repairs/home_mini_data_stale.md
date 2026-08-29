# Repairs - Home Mini data has stopped updating

This repair is raised when the integration has not received new consumption data from your Home Mini for at least 30 minutes. The integration retains the last good data internally, stops recalculating live entities from it while it is stale, and removes the repair automatically when current data becomes available again.

First, check the live usage feed in the Octopus Energy app or website. Home Mini data is retrieved from Octopus Energy's servers, not directly from the device, so missing data there cannot be recovered by the integration.

If the live feed is also stale, try power-cycling the Home Mini and check that it is connected to Wi-Fi and can communicate with your smart meter. If it does not recover, contact Octopus Energy support.

If the Octopus Energy live feed is current, check whether another app or integration is using the same API credentials. Octopus Energy applies a shared API rate limit, so you may need to increase the [Home Mini refresh interval](../setup/account.md#refresh-rate-in-minutes). If the issue continues, [raise an issue](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues) with your integration diagnostics and an hour of debug logs.
