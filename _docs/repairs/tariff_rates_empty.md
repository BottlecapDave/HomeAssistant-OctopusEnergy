# Repairs - Tariff Rates Empty

If you have received this repair notice, it means you have one or more meters associated with a tariff that no longer appears to be returning up to date rate information. 

This can be confirmed by looking at the rate feed. For example if you have tariff 'G-1R-SILVER-25-09-02-M' and product 'SILVER-25-09-02', then for electricity you can find the rates at https://api.octopus.energy/v1/products/SILVER-25-09-02/electricity-tariffs/E-1R-SILVER-25-09-02-A/standard-unit-rates/ and for gas you can find the rates at https://api.octopus.energy/v1/products/SILVER-25-09-02/gas-tariffs/G-1R-SILVER-25-09-02-A/standard-unit-rates/. If the first record has an "valid_to" value that isn't "null" and in the past, then new rates are no longer being published.

This can occur for a number of reasons

1. Your tariff has finished but you haven't been moved to a new tariff for some reason.
2. There is an issue with the rate feed. This might be a short term issue with the Octopus Energy servers, so waiting my rectify the issue.

To rectify all of these issues, you will need to contact Octopus Energy to fix this issue.