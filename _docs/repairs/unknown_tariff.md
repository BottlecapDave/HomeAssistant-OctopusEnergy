# Repairs - Unknown tariff

If you receive this error around one or more of your tariffs, it's because the Octopus Energy API can not find the tariff. This usually occurs if your on a tariff which is currently internal and has not been exposed. In this scenario, there is nothing I can do and you'll need to contact Octopus Energy either via the email located on your [account dashboard](https://octopus.energy/dashboard/new/accounts/personal-details/api-access), or by raising an issue in their [forum](https://forum.octopus.energy/). Below is an example of what you're requesting.

```
Hello,

I'm using the Home Assistant Octopus Energy integration (https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy) which uses your APIs. I am on tariff "<<INSERT TARIFF HERE>>" and it is unable to find either the tariff or the associated product at `/v1/products/{product_code}`. Can you please find out why the product is not available.

Thanks
```