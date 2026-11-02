# Account

Entities relating to the account as a whole.

## Account Balance

`sensor.octopus_energy_{{ACCOUNT_ID}}_account_balance`

The current balance of the account in pounds. A positive value means the account is in credit, and a negative value means the account is in debit. The balance covers all ledgers on the account.

Data is refreshed every 60 minutes. Each time the balance is retrieved, the [account balance event](../events.md#account-balance) is fired.

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). It is only available if the account has at least one electricity or gas meter point with an active tariff.

| Attribute | Type | Description |
|-----------|------|-------------|
| `last_transaction_date` | `date` | The date the latest transaction was posted. The balance includes all transactions posted up to the end of that day. `null` if the account has no transactions |

## Account Balance Events

`event.octopus_energy_{{ACCOUNT_ID}}_account_balance_events`

The state of this sensor states when the account balance was last retrieved. The attributes of this sensor expose the data from the [account balance event](../events.md#account-balance).

!!! note
    This is [disabled by default](../faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). It is only available if the account has at least one electricity or gas meter point with an active tariff.

!!! note
    The account balance is only retrieved while the account balance sensor or its [data last retrieved sensor](./diagnostics.md#account-balance-data-last-retrieved) is enabled. Without one of these enabled, this entity will not receive any updates.

| Attribute | Type | Description |
|-----------|------|-------------|
| `account_id` | `string` | The id of the account the balance is for |
| `balance` | `float` | The balance of the account in pounds. Positive is in credit, negative is in debit |
| `last_transaction_date` | `date` | The date the latest transaction was posted. The balance includes all transactions posted up to the end of that day. `null` if the account has no transactions |
| `transactions` | `array` | The most recent transactions on the account (up to 10), newest first. Includes bills, payments, refunds and credits |

Each transaction item will include the following attributes. Any of them, other than `type`, can be `null` if Octopus Energy does not provide a value.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `string` | The id of the transaction |
| `type` | `string` | The type of the transaction. This will be one of `charge`, `payment`, `refund` or `credit` |
| `posted_date` | `date` | The date the transaction was posted |
| `title` | `string` | The title of the transaction, if available |
| `amount` | `float` | The amount of the transaction in pounds, as reported by Octopus Energy. The sign depends on the type of transaction; for example, export earnings appear as negative charges. Use `balance_after` to see the effect on the balance |
| `balance_after` | `float` | The balance Octopus Energy reports after this transaction was applied, in pounds. Positive is in credit |
| `is_export` | `boolean` | Whether the charge is for export. `null` unless the transaction is a charge |
| `consumption_start` | `date` | The first day of the consumption the charge covers (inclusive). `null` unless the transaction is a charge |
| `consumption_end` | `date` | The last day of the consumption the charge covers (inclusive). `null` unless the transaction is a charge |
| `consumption_quantity` | `float` | The amount of energy consumed. `null` unless the transaction is a charge |
| `consumption_unit` | `string` | The unit of the consumption. `null` unless the transaction is a charge |
