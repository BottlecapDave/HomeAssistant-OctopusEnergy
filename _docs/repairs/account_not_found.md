# Repairs - Account not found

If you receive the fixable warning around your account information not being found, there are two possible causes and solutions

## API Key is invalid

The simplest cause is that your API key has become invalid. This can happen if you have recently reset your API key in your [Octopus Energy dashboard](https://octopus.energy/dashboard/new/accounts/personal-details/api-access).

To fix
1. Navigate to [your integrations](https://my.home-assistant.io/redirect/integrations/)
2. Find 'Octopus Energy'. If you have target rate sensors set up, click on the entry marked either 'Octopus Energy' or 'Account'.
3. Click on 'Configure'
4. Update your API key with your new one displayed on your [Octopus Energy dashboard](https://octopus.energy/dashboard/new/accounts/personal-details/api-access).
5. Click 'Submit'

## Account id is invalid

If you have setup the integration with an account that is no longer valid, you will need to manually remove all entries for the integration.

To fix
1. Navigate to [your integrations](https://my.home-assistant.io/redirect/integrations/)
2. Find 'Octopus Energy'.
3. If you have no target rate sensors setup, click on the three dots and then click on 'Delete'
4. If you have target rate sensors setup, click on each entry within 'Octopus Energy', click on the three dots and then click on 'Delete'

Once done, you can then add the integration fresh with your new account.