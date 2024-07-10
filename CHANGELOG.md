## [11.2.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.2.1...v11.2.2) (2024-07-10)


### Bug Fixes

* Fixed division issue with cost tracker when an update event is fired but no change is detected (30 minutes dev tim) ([c0eba23](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c0eba23f44a749711b689f396efc276ae05c81d3))
* Fixed initialisation issue when only gas is supplied by OE (Thanks [@ksimuk](https://github.com/ksimuk)) ([1823628](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1823628193ee3be1a050d6a2bfeffada39138c3f))
* Fixed issue where current consumption sensors were not available if you configured only a Home Pro (30 minutes dev tim) ([6499cc1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6499cc1d72bdb43a27b2ad1e157853eef462ec01))
* Improved Home Pro error messages (5 minutes dev time) ([c5e6968](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c5e69686ce4b25c0487c1524376310e06ddcebd6))
* Separate stopping demand sensor from updating if total consumption is not available from Home Pro (30 minutes dev time) ([a03cfab](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a03cfab83baa7a8d5c1519a98a5215d8b060676b))
* Sort meters by most recently active to account for switching meters (15 minutes dev) ([27c39af](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/27c39af46e749f6b0e8a313ce338d956975bfd06))

## [11.2.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.2.0...v11.2.1) (2024-06-29)


### Bug Fixes

* Fixed calculating total gas consumption from Home Pro when reported in cubic meters (1 hour dev time) ([09965b5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/09965b5d90b8bdd8606880ecbacb2de908d48190))
* Fixed issue where home pro could not be unset ([2d419c9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2d419c99df7d642d8d1d6e2e975a09eb53bf7294))
* Fixed issue where old inactive meters were being registered (1 hour dev time) ([9ab2bf7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9ab2bf79954bd3f94c45e51cc52dbd5e0591d035))
* Improved Home Pro connection errors (30 minutes dev time) ([40582ae](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/40582ae801e770e854a5727cca628906dc679019))
* Updated home pro installation command (Thanks @DJBenson) ([5502619](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/55026196aaa6e8744b63a81a4fe5274f15d4b305))
* Updated home pro to ignore total_consumption of zero (15 minutes dev) ([4a110f3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4a110f36b96c0bb018df08468c87df22f4bc190b))
* Updated home pro to report None if demand not available ([fd4cbbb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fd4cbbb0abc946aef84e4c9eabf8fe3f8bc3ade6))

# [11.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.1.1...v11.2.0) (2024-06-16)


### Bug Fixes

* Add threshold for cost tracker to allow tradcked total_increasing sensor to decrease slightly without treating it as a reset (30 minutes dev) ([0de0bb3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0de0bb3f36bf92d0abc1a78e7148ce179bd09dc0))


### Features

* Added experimental support for Octopus Home Pro (3 hours dev time) ([2560b6b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2560b6b6597d4e1e6e4c66c9e2aeadcf95a0c5be))
* Added sensors for displaying current total consumption (40 minutes dev) ([dbb2b5d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dbb2b5da5956aa07a77211e0acbe5f6590a13351))
* Updated intelligent charge limit to be an input box rather than slider ([778f197](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/778f19774794f0506d2936524ec7d04feb0ce84f))

## [11.1.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.1.0...v11.1.1) (2024-06-12)


### Bug Fixes

* Fixed support for duel rate tariff that doesn't conform to normal structure (30 minutes dev work) ([3951db9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3951db981f1c9dfefa3d780159e8d91ebc5676ea))

# [11.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.0.2...v11.1.0) (2024-06-10)


### Bug Fixes

* Added some additional checks around cost tracker attributes ([79d339c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/79d339c4446a775304568d6bfd1cff4f9da80939))
* Fixed spin wheel of fortune service ([42a0f65](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/42a0f65ebed7f2493dbcc8e7abc4a8758aa0ef0a))
* Made tariff rate unique calculations more resilient to incomplete rate information ([3b8ce91](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3b8ce91dc32f6d763bd79a3dd4a7efd025788c4d))


### Features

* Added ability to compare multiple tariff which supersedes current overrides (4 hours dev time) ([effba64](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/effba64d7b1aec46ea328ef7a4653b24c41bd393))
* Added repair notice for when API key has become invalid (1 hour dev time) ([6a49f60](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6a49f608bc4158a07b15b3f36f74a030d5eb80b8))
* Added repair notice if rates change to a state where new entities become available or existing entities are no longer applicable (1 hour dev time) ([e207c23](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e207c23df70198c38586e49a001745544dd0015c))
* Added support for business tariffs (5 hours dev time) ([804cd9d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/804cd9d02ca40ba5145af273405188ab29ec3db4))

# [11.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.0.2...v11.1.0) (2024-06-10)


### Bug Fixes

* Added some additional checks around cost tracker attributes ([79d339c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/79d339c4446a775304568d6bfd1cff4f9da80939))
* Fixed spin wheel of fortune service ([42a0f65](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/42a0f65ebed7f2493dbcc8e7abc4a8758aa0ef0a))
* Made tariff rate unique calculations more resilient to incomplete rate information ([3b8ce91](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3b8ce91dc32f6d763bd79a3dd4a7efd025788c4d))


### Features

* Added ability to compare multiple tariff which supersedes current overrides (4 hours dev time) ([effba64](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/effba64d7b1aec46ea328ef7a4653b24c41bd393))
* Added repair notice for when API key has become invalid (1 hour dev time) ([6a49f60](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6a49f608bc4158a07b15b3f36f74a030d5eb80b8))
* Added repair notice if rates change to a state where new entities become available or existing entities are no longer applicable (1 hour dev time) ([e207c23](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e207c23df70198c38586e49a001745544dd0015c))
* Added support for business tariffs (5 hours dev time) ([804cd9d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/804cd9d02ca40ba5145af273405188ab29ec3db4))

## [11.0.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.0.1...v11.0.2) (2024-05-18)


### Bug Fixes

* Reverted requirement for target sensor to have target hours above zero (30 minutes dev) ([0098efa](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0098efa7151808deb9b2a73a69b39a19f7b86208))

## [11.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.0.0...v11.0.1) (2024-05-18)


### Bug Fixes

* Fixed export suffix for electricity meter device (1 minute) ([7c7d999](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7c7d999c05254f8a272dbc90d50ac689db932407))
* Fixed issue where old target rates are present when config is updated (45 minutes) ([6aeada6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6aeada69944802e25b29309e393d5a8b27a8da15))
* Fixed issue where start, end and offset could not be unset for target rate config (15 minutes) ([cb170af](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/cb170afa78de0940c17b333b76708ef5e9c834e8))
* Fixed refreshing gas consumption data service (15 minutes) ([fbe3f46](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fbe3f468c2a35928dd1142be346590e47fa444e3))
* Fixed target rate sensor not being able to set zero hours (20 minutes) ([022f30d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/022f30db7895f986cfd94fdefa5a51b2b1c8a0d5))

# [11.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.3.1...v11.0.0) (2024-05-12)


### Bug Fixes

* Accounted when intelligent device can come back with null data from OE ([53db610](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/53db610134fbb4356603b76634c56f71304280f7))
* Fixed issue when str error reported if config of target rate sensor fails first time ([c5cfd83](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c5cfd8310ad196b666d6ff3ed5c28fc6587e2b1b))
* Fixed issue with dispatching sensor if rate is off peak from now until the end of the available rate data ([c583b8b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c583b8b54c483ab6e6770e01b13b886511aa1596))
* fixed tariff override data having rate value in pounds and pence for consistency ([48f832a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/48f832afd9cb5ea846d655e7eb3ea7937520822b))
* Fixed updating cost tracker config ([c934614](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c934614ccd0a9b5ee471280be2c0d565000a9c52))
* Fixed warning for deprecated EventType reference ([e8786df](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e8786df9fb476a56fd4a4347f03ab46075c02be7))
* Limited backoff logic to 30 minutes between attempts so it doesn't increase forever ([f2de64d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f2de64d2ac176c26e7224b6ddeae04cf5f85d6ea))
* Updated attributes and events to have datetimes in local time (UTC in winter, BST in summer) ([19ac60f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/19ac60f10ae81f4a81bedbd448c5563c41e35805))
* Updated minimum Home Assistant version to 2024.5.0


### Features

* Added ability to configure optional minimum/maximum rates for target rate sensors ([95ac448](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/95ac4489653a97cd2a3d3274908543d73ff5827f))
* Added support for applying weightings to target rate slots ([80bbb52](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/80bbb52b413aa722a5a4a5eac654901fd51185f7))
* Added support for tracking 3 rate tariffs (e.g. Cosy) via separate sensors ([40d21d1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/40d21d1815ceb9f1e1eff1be7362b42b15950668))
* Added the ability to delete devices manually ([404d2e9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/404d2e9edef494348dfc9e95c86d0b410746f548))
* updated the default names of various sensors to be more useful in areas of HA when space is limited ([870c917](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/870c917fd4a166ea71a51971df9b98e7d75957bd))


### BREAKING CHANGES

* If you are relying on the previous default names of sensors then you will need to update your
sensors manually. Only the visual default name of the sensors have changed; the entity ids will
remain the same and therefore will not effect any automatmations. If you have manually changed the
names of the sensors, this should not effect you.
* For 3 rate tariffs (e.g. Cosy), the peak based sensors will no longer track consumption/cost for both peak and standard rates. There is now a third sensor (standard) which tracks the middle rate. In addition, if you are on a tariff that doesn't have off peak, standard or peak rates, the current off peak/peak based sensors will no longer be provided by the integration.
* If you were relying on datetime based sensor attributes or event properties being in UTC, you will
need to adapt accordingly
* If you were using tariff override rate information, you may need to adjust your use due to changes
in how value is reported

## [10.3.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.3.0...v10.3.1) (2024-04-20)


### Bug Fixes

* Removed excessive logging that did not adhere to log settings ([cb27d6d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/cb27d6de4601d36e6527fb76945fec2bb444c0ee))

# [10.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.2.1...v10.3.0) (2024-04-15)


### Bug Fixes

* Fixed account setup descriptions to be clearer ([4107fb7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4107fb714fec41de2286223f5f664fe787f19068))
* Fixed peak/off peak cost calculations during BST time period ([11d5a9f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/11d5a9f601f937052a9bf0e2785300b06bb4f34f))
* Fixed peak/offpeak consumption/cost sensors going into negative on energy dashboard ([c167f39](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c167f39a7c99ae5126cfacdedeeab86fd0ec3ac9))
* Fixed rate min/max/average calculations during BST ([fdccc5b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fdccc5b86031c01afd09cc0fa2613f7c9802411c))
* Increased minimum required version of home assistant ([e662659](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e662659aea551e9fdbf92268b2d703ab9d3cbd69))
* Updated electricity rates to not update initially until dispatch rates have been retrieved if on intelligent tariff ([756535e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/756535eb5c950d995a342f344cabf462177febf3))


### Features

* Added duration in minutes to saving sessions ([35d17dc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/35d17dc61df7879557e4ab8ec85cff61f874c9ce))
* Added redeemable points attribute that determines how many points can be converted into account credit ([9d1233d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9d1233da6db055447aa68b293564ed834b9853cf))
* Added service for redeeming octoplus points for account credit ([0390a33](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0390a33b89498f05fbeb9c6b413119bea2d43a3a))

## [10.2.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.2.0...v10.2.1) (2024-04-07)


### Bug Fixes

* Fixed logging issue with cost trackers ([cfdd927](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/cfdd927ab0b94be9554cb7458789e9034c6605a5))
* Fixed target rate sensor picking times an hour before/after requested timeframe - timezone issue ([3651780](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3651780af51ba37c85f357925631174a298feed3))

# [10.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.1.4...v10.2.0) (2024-04-06)


### Bug Fixes

* Added missing account id information for previous accumulative gas consumption sensor ([6bd6387](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6bd63871d1ad77ceb9c12f5e8696b725b1d77a00))
* Fixed issue when consumption data from Octopus Home Mini is not defined but demand data is ([d51647c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d51647c2962d0f09c96ee81e9fa369879f901875))
* Fixed missing account id for repair message relating to octopus mini not being available. ([fa5650f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fa5650faf8726d81c1ed1bf2b8c6c222a8dab59b))


### Features

* Added attribute to previous consumption sensors to indicate the latest available data via the API ([cd735c6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/cd735c6c2ac0eb60ceb44f9dcf9629ece91cf701))
* Added cost tracker for weekly and monthly accumulations ([01c3733](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/01c3733111abeceff2edba2a0074fc49a279b41f))
* Added sensor for next greenness forecast ([0708271](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0708271eb5bf919d57e7fc421fbc5dbdd2fd10c3))
* Added service for adjusting specified dates within cost tracker accumulative sensors (e.g. week and month) ([26a9462](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/26a946228a1fc47fa82c1020584b4762b9973c91))
* Added service for adjusting standard daily cost tracker ([1378e47](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1378e4708e4846b46e05ec2fa557f04c49cb01fa))
* Added service for resetting a cost tracker back to zero. ([d28d63b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d28d63b17dec9d43604f44d96ead6dc35f9a967f))
* Added support for multiple different accounts ([c15b4af](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c15b4af83b7075631871a7069f734b823c7e3504))
* Updated cost tracker config to be updatable ([c24db54](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c24db54df842d09ed86f383d2eca1bfd5c5e0342))

## [10.1.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.1.3...v10.1.4) (2024-02-22)


### Bug Fixes

* Fixed invalid reference ([0083b2d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0083b2df5de510c3a4fc8d2ae9d72563cd9f9abd))

## [10.1.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.1.2...v10.1.3) (2024-02-22)


### Bug Fixes

* Fixed issue when dispatch source is not defined to count as smart charge ([0af23b9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0af23b98d1702a847354b5bf28cec11507c551ea))
* Fixed issue when dispatching sensor would not stay on during full half hour when planned dispatch is active ([e64c694](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e64c69484dbdba271c5d3dd0adaeb7b839ff8b1b))
* Fixed issue where start/end times could be incorrect on next/previous rate sensors ([c431dac](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c431dac82e4172cbfc2ed9e59faa831ef1523e55))
* Fixed issue with calculating current rates for intelligent based tariffs ([6efcfc0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6efcfc0fd10eb5d23f4e2fb62ae04bfa28d26018))

## [10.1.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.1.1...v10.1.2) (2024-02-18)


### Bug Fixes

* Automatically removed devices associated with old meters ([e6905d0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e6905d096373ed40b6f8a7fb0cd62c4a8bd436a2))
* Fixed dispatching sensor incorrectly turning on when bump charges are activated ([b37e4b1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b37e4b1a4ae5447ebc8465839eb9c0c1a9f4be5c))
* Fixed issue where client is not cleaned up correctly on restart ([deac67b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/deac67ba099c251c4b21bc11ab32d7bd480548a1))
* Fixed issue with cost trackers when old state is unavailable/unknown ([599613b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/599613b6b4e4b5aa70670e2dd653f3f3f88ae605))

## [10.1.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.1.0...v10.1.1) (2024-02-17)


### Bug Fixes

* Fixed icon for update cost tracker service ([e1d048a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e1d048a1fc99655000163931f38b680a66915aa0))
* Fixed issue when rates were not adjusted for dispatches that started or ended part way through a rate ([fb3e3f2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fb3e3f2cf269a90c01b97162729dba2db98b8aa1))
* Fixed issue where previous cost is calculated incorrectly when on restart and on intelligent tariff and dispatches have not been retrieved ([406f2c8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/406f2c84f392d17e9fd836597ecda00f8e95c47d))
* Fixed issue where tariff attribute on entities would be old tariff when switched over ([a328fec](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a328fece656eda5a5f0bf432b3ef290517abab07))
* Fixed issue with cost tracker when used with total_increasing entities that reset ([6759317](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6759317099328d185cd4fa05fdc628f29b6b0d04))
* Fixed previous consumption cost not adapting when tariff changes ([2ec461e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2ec461eb1616f2f10ab583ba561823202bbf6706))
* Updated saving sessions to ignore octopus test events ([9488a37](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9488a370b0d703fe68eb34f9e4222fd18ff5d0ec))

# [10.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.0.4...v10.1.0) (2024-02-10)


### Bug Fixes

* Fixed charge limit sensor to behave like the app around accepted values ([c42a619](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c42a619fdffeee0c6e28fec92070396132146ebc))
* fixed issue with override costs getting stuck ([1b93638](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1b9363863a4e3f9567fd0d6060a1dd7d4e2270cf))
* Fixed issue with rate sensors not updating properly when intelligent dispatches update short notice ([f1623e5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f1623e5af0e36193f41d4abfab406e1036d528b1))
* Fixed issue with refreshing previous consumption and database lagged behind processing ([fbe9896](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fbe9896e1711586398070b19a728847182c8aedc))


### Features

* Add icons for services - Thanks [@andrew-codechimp](https://github.com/andrew-codechimp) ([0ef0a7c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0ef0a7cfad2da1cf14c9d8bb2f7177cf104420a1))
* Added greenness forecast support ([872711e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/872711eb23b1d14434d6421a9328aeb757b59776))
* Updated dispatching sensor to include current start/end and next start/end attributes ([e2ed003](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e2ed00340dc4d94ba5700c03589a875518c89541))
* Updated off peak sensor to include current start/end and next start/end times as attributes ([8da4679](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8da46796871283227d3e96bd05eb65a70b755df7))

## [10.0.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.0.3...v10.0.4) (2024-01-29)


### Bug Fixes

* Added additional check in electricity rate calculations ([1e30999](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1e30999b0ff030de8bf6310e8000fbb40c75b4a6))
* Fixed current consumption sensors not updating if other sensors were disabled ([443a130](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/443a13075d5719cc20a4d1d38e4fd9350fe9c89a))
* Fixed issue with binary sensors not restoring previous state correctly ([5c85dae](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5c85dae64b59d7d3c467fe6f8cf822acb040a1da))
* Fixed restoration of entities to handle "unavailable" state ([248e700](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/248e70099d462912cd29f8d5009124d04c9e0c86))
* Fixed target rate setup when invalid start/end time is set and on agile tariff ([fe1bad1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fe1bad197a7607b4763a515b849cb1ef6e1dd2cd))

## [10.0.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.0.2...v10.0.3) (2024-01-20)


### Bug Fixes

* Fixed current consumption not resetting to zero at midnight if data isn't available ([19ae707](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/19ae7074ead4e3ff6da210c7e027d831cab2a675))
* Fixed current consumption sensor resetting to zero after a minute when data hasn't refreshed ([a13edef](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a13edef4fb8af213334fddd05a1f2aed40b2c898))
* Fixed issue intelligent based electricity rates not being adjusted when dispatches are refreshed between rate refreshes ([f9514d3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f9514d3e068548ee20bfb189abad2d76bd92d2ef))
* Fixed issue when updating electricity rates and intelligent dispatches is unavailable ([9bd2b9c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9bd2b9c74046a54684a5c7d4100e18c30a613eaf))
* Fixed old Intelligent Go tariff not being picked up correctly ([c935206](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c9352060b10799c43941d7e322663593f718bf0a))
* Increased timeout limit to 20 seconds to try and resolve issues people have been having ([6de26f6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6de26f69a40decb816b8193511db44ebae7ddcc6))
* Removed duplicate logging of events ([1f4e3da](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1f4e3da9f89ae615d44b38eee7e916d4e7608308))
* Reset cost tracker every day at midnight ([3328562](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/33285628bb618ab3a2072f3fcb5e09769c27757f))
* Updated various sensors to update their state based on recommended HA practices ([9885528](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/988552865909d137e6ea85639cd364f073468546))

## [10.0.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.0.1...v10.0.2) (2024-01-07)


### Bug Fixes

* Removed entity migration as not working properly and putting things into weird state. Follow https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/discussions/678 for updates ([daa492f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/daa492ffbf2c83de78623b0268220841dc117d8b))

## [10.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.0.0...v10.0.1) (2024-01-06)


### Bug Fixes

* Added migration of accumulative gas consumption sensors - see https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/discussions/678 for more details ([f379786](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f37978673aec21f008d8d35c7bcfcba48bd59173))
* Fixed being unable to edit target rate configuration ([150d97a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/150d97af9149affa456801a30895f7e6b3be327f))
* Fixed initialising of integration to automatically retry if account information can't be retrieved ([320eb15](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/320eb15cc1fd1ff3039aaa0abfa7bc4f1c35ff6d))
* Fixed issue when intelligent device provider is unavailable ([6d9f469](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6d9f4693b335aa84caaaf4885d32fb9300921231))
* Fixed warning raised in charge limit sensor ([c43ef73](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c43ef73abb7553aec89985acf88b5672cbaaa6bd))
* Fixed where intelligent entities were incorrectly available to users on intelligent flux tariff ([0be466a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0be466a578f910e2af79ed3ccd63b26bdf3fd35e))

# [10.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v9.2.1...v10.0.0) (2024-01-04)


### Bug Fixes

* Added prevention around multiple access token requests ([0ecd453](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0ecd45325f90c4ad1599b0f73a305fb23982d354))
* Fixed deprecated HA references ([5751d3b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5751d3b0b301e18f60755aec56358bbc1152e087))
* Fixed issue with cost override when last retrieved is not defined ([59dbb7d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/59dbb7df4531e6c1ae50ba1583602d4fd3b5344a))
* Fixed off peak sensor turning on during extended intelligent off peak periods ([9b36f07](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9b36f07b5d53d05e82cac518748ae0013f320576))
* Fixed restoring of intelligent states ([faa3a32](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/faa3a32e942c5c57241e19e1fe18dde1d8802a66))
* reduced API calls for intelligent data during setup ([381c723](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/381c723885d2b068b4a4f2b9dd15883460861588))
* Reduced required data on startup to speed up initialisation. This may result in a slight delay to get updated data ([5a2838f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5a2838f3c61b688149d106ba42b9169d1c518206))
* removed various intelligent features for OHME as these were incorrectly exposed and not supported ([9d52884](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9d528841b992328d490bd1e051c58625d8fba270))


### Features

* added m3 representation of current accumualtive gas consumption for Octopus Home Mini ([bc1be66](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/bc1be661dde383598812b92cd9ff03f05462e5cf))
* Added min/max/average rates to previous/current/next day rate events/entities ([58c3488](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/58c34885bc2125074b574112fbef477a56b635bf))
* Added support for custom sensors for tracking the cost of other entities ([54604fd](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/54604fdb0c7f24cb65346010f00e299c3dd1e0df))


### BREAKING CHANGES

* The current and previous accumulative gas consumptions meter entity ids have been updated to include
suffixes representing the reported unit of measurement. Any references to these entities will need
to be updated.
* If you are on intelligent tariff and use OHME chargers, then various intelligent features will be
removed. These were incorrectly exposed. Please see
https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/573 for more information

## [9.2.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v9.2.0...v9.2.1) (2023-12-20)


### Bug Fixes

* Fixed issue where user agent version was not updated ([6660075](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/66600758be135ab0a58a43ec4378ab6026bc6ea1))

# [9.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v9.1.0...v9.2.0) (2023-12-19)


### Bug Fixes

* Added missing translation for target rate config ([eb7c892](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/eb7c892ed3e05c4233f63b27ef458396b7d33073))
* Fixed issue with target rate when offset is applied twice to next time value ([20a1a8c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/20a1a8c322dda994e3a5cd51222d5c346013702e))
* Updated account config to include instructions for where to find account id and api key ([a409889](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a409889d723297ee0c0211252bc04d1000b2eb27))


### Features

* Added indicator to target rate sensor to indicate if rate information is incomplete and therefore target times cannot be calculated ([28676c3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/28676c38c9da81936137b166dd311ed782f76813))
* Improved how data is retrieved from APIs and added backoff logic when failing to contact APIs ([d461718](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d461718504243bcd0d6e304c85eb21d7967d54fc))

# [9.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v9.0.2...v9.1.0) (2023-11-28)


### Bug Fixes

* Added checks to ensure current gas consumptions were not negative ([b8418e1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b8418e13636c8a2fee2d960fd22fda8eabfe257c))
* Added defensive logic around loading of local completed intelligent dispatch data ([4049c6d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4049c6d10eb563d2615cbf83ebf30a7303138c19))
* Fixed expectation that charge_in_kwh is available in local intelligent dispatch data ([6e0c3ed](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6e0c3edff68d10fdf447025cb683937b57595721))
* Fixed issue where event entities were not being restored properly ([00ec35c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/00ec35c18767243dd448d1f1f817cabe89bb13ed))
* Fixed octoplus points sensor to not be available for users who have not enrolled on the programme ([3476fae](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3476fae9b88b0c235b49e65e871e8e395b4d3682))
* Fixed restoring of attributes on target rate sensor ([7a384ef](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7a384efdbe348d828e8e14fd807fc83563ca2983))


### Features

* Added octopoints_per_kwh to joined saving session events (if known) ([350ad20](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/350ad20ccbae8c0e4360053d2af8bb4098e833d7))

## [9.0.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v9.0.1...v9.0.2) (2023-11-25)


### Bug Fixes

* Fixed issue with current consumption sensor not working properly in energy dashboard ([08af21b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/08af21b618d092c7a1e548193319dfdbbc9aac6e))
* Fixed issue with not being able to unset price caps that were set when the integration was configured initially ([838f2e3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/838f2e30f6c63290935cd717c4fc21da0fc32f69))
* When using the join saving session service, related data updates are forced in the next cycle ([626c1c1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/626c1c19ef908f45889ea62a108e6d44f8094f87))

## [9.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v9.0.0...v9.0.1) (2023-11-22)


### Bug Fixes

* Fixed issue where all previous day rates are not retrieved for agile tariff ([1ff0ce9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1ff0ce9cc0b641616756b1a4c3c26872966aa26f))
* Fixed issue where restore state was set to invalid unknown value ([24c09d6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/24c09d66e42f8c0e4385e2020ef16fda33dd62ef))
* Fixed refresh_previous_consumption_data for gas to populate kwh data ([e5b3a3e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e5b3a3ecf651eb8b88cfab5eb45bdf9504565c93))
* Removed stale last_updated_timestamp attributes ([763842f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/763842fff41e5e5357acbd5a3d9267813130bc06))
* Updated previous/current/next event rate sensors to not be disabled by default ([e10c6dd](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e10c6dd2e1a7753e70ed8dbddd35fb6515f77458))

# [9.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.5.2...v9.0.0) (2023-11-20)


### Bug Fixes

* **custom:** updated value_inc_vat and rates to be in pounds/pence for consistency ([439c081](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/439c08162ff1ac6e2d04572bfbde141c5f717a42))
* Fixed issue calculating off peak costs when rate information isn't available ([fc155a1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fc155a1317fd0a078d45e11eb05b25ef6e9c4aa0))
* Fixed issue when failing to retrieve account during setup ([c9d04fb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c9d04fb9573114dc9c4c79846d3b65eac73a4302))
* fixed issue where sensor attributes were always strings when restored after reload/restart ([53964ae](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/53964ae57e9420608651e8a1e3950608edd82c0a))
* Fixed issue where unit of measurement couldn't be changed/converted within HA ([f07da9d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f07da9d47e2ce66534ff1451afb1c2c7d3b4bb54))
* removed all_rates and applicable_rates attributes from rate sensors to fix statistics warning ([280e6d2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/280e6d25fcb18ce17df158734f9cba3cd7d92574))
* updated standing charge attribute on cost sensors to be in pound/pence for consistency ([913336a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/913336a3ecb9e0a3fdccc01132db3e930968a016))


### Features

* Added new events for new and all saving sessions ([b2b44b5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b2b44b5697611e48b446a1066c4c7f8a41ef8a32))
* added new sensor for octoplus points ([800fc85](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/800fc8597d981090b87b1f659f924893f7215662))
* Added sensors for available wheel of fortune spins ([6273784](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6273784f03096a484105cb282439efae604d527c))
* Added service for joining a saving session ([01342b5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/01342b58851214da6a3559f3d6385916f3f76365))
* Added service for spinning wheel of fortune ([effcc21](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/effcc2147e5266491c3eacb25adeff0c7e673966))
* Added two new attributes to various sensors determining when the underlying data was last retrieved and when the value was last evaluated. These will slowly be added to other entities. ([11f8878](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/11f887815eec47c3665e0bb36641ac36da036427))
* created new event entity to capture available and joined octoplus saving session events ([b402c06](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b402c06e4ebe648aa0f4dd0d92da9a26809cdd2f))
* standardised attributes around time periods across the integration ([89a6985](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/89a6985af4647ce4cd7954a7f8d77a60a3260c0d))
* standardised attributes around time periods across the integration ([#535](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/535)) ([7f6712f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7f6712feb7312cbd7260293258435f7d3a1415ce))
* Updated config entry for account to have the account id as the title ([02ef313](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/02ef3131c437fee345a39f8c2a73e5e75acbdeb9))
* updated intelligent sensors to include account id. This is to support future functionality ([57e3d79](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/57e3d7929fddf863e47ba1c2408b3ac8e2acd8a8))
* updated last_calculated_timestamp attributes to last_evaluated for consistency ([702eb4a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/702eb4a42893afe28caeccf4d3add1be99138a1c))
* Updated saving session sensor to include account id. This is to support future functionality ([3136005](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/31360056bc8d95098a85fe6bc349c8a3bb84f415))
* Updated underlying config with some missing fields ([82e4564](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/82e4564bbaf40926a827392f73dc8f08d3fe23b7))
* updated various attributes to be their numberic value instead of strings with symbols ([727db53](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/727db53912eea34d4c778ee2337d4fe9388405d4))


### BREAKING CHANGES

* all_rates and applicable_rates attributes are no longer accessible in rate sensors. All rate
information is available in the events attribute. See
https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/discussions/444 for more information
* Any previous references to valid_from/valid_to,
interval_start/interval_end or from/to have now been changed to
start/end. This change may take a little while to propagate while old
data is replaced. Any reliances on these attribute names will need to be
updated.
* The joined events attribute has been removed from the saving session binary sensor in favour of the event entity
* Any references to last_calculated_timestamp attribute should be updated to last_evaluated
* saving session points sensor has been removed in favour of octoplus points sensor
* Any references to saving session entities will need to be updated based on name change including account id
* Any references to intelligent sensors will need to be updated based on name changes including account id
* All references to value_inc_vat and rates are now in pounds/pence. If you are relying on this
structure, you may need to update your logic
* Standing charge attribute on cost sensors are now in pound/pence. If you are using this, then you may
need to adjust any calculations etc.
* Various attributes have been updated to be numeric instead of strings with symbols (e.g. £1.50 -> 1.50). Any
logic that was used to remove these symbols will now break. In addition, some attributes had raw
representations, which have now been removed. Please review docs for more information.

## [8.5.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.5.1...v8.5.2) (2023-11-08)


### Bug Fixes

* Fixed previous consumption peak/off peak sensors ([b3d4f6f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b3d4f6f876f0d3630bedec350e20c7c7c9f541f5))

## [8.5.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.5.0...v8.5.1) (2023-11-02)


### Bug Fixes

* Fixed retrieving previous electricity consumption for intelligent tariffs ([40651a2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/40651a245dc3b40d84ea0d01ba2df39115f2826a))
* Fixed target rate sensor restoring old settings ([ec40fe2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ec40fe2503d7776c1c9ef6b8ec867aee4011887a))

# [8.5.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.4.4...v8.5.0) (2023-10-29)


### Bug Fixes

* Added check when configuring home mini, to make sure home mini support is actually available ([770edc4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/770edc470b2ce0ae675a99598d3985fd3f0beb49))
* Fixed clearing of price caps without needing checkbox ([f5fbc0c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f5fbc0cea9b4f65692a2998c3a3f340ebe65f909))
* Fixed off peak detection for octopus flex (should never be applicable) ([912efd7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/912efd7f7fc4f7d50af665b07c2f80a55b6b7a2a))


### Features

* Added last evaluated attribute to target rate sensor for more clarity ([fd5395d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fd5395da9901740983e8d2093396bdbc17c1f6ad))

## [8.4.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.4.3...v8.4.4) (2023-10-14)


### Bug Fixes

* Added explicit timeout to OE server requests ([b516e4a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b516e4a54774f393d55a46921c2fa511505d5c6d))
* Fixed intelligent coordinator update frequency (thanks @Pixel-Gavin) ([8e1f80c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8e1f80c104405c7adf7b2992256dc87408619d45))
* Fixed update interval for data coordinators to be minutes not hours ([830604d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/830604d3347c56b93fe42e30e0bb875ca025e2e4))

## [8.4.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.4.2...v8.4.3) (2023-10-12)


### Bug Fixes

* Fixed intelligent settings reverting if multiple changed in quick succession ([0a4c95b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0a4c95badbc29dbe3adf6c65cf480702b819b46f))

## [8.4.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.4.1...v8.4.2) (2023-10-09)


### Bug Fixes

* Updated minimum version of Home Assistant to 2023.09 ([30157c0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/30157c0a7af8b6c519800393329413a2298e8272))

## [8.4.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.4.0...v8.4.1) (2023-10-07)


### Bug Fixes

* Fixed error in dispatching sensor ([0799002](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/079900299ce2500b440d32d6e309e03fb2da60cf))

# [8.4.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.3.0...v8.4.0) (2023-10-07)


### Bug Fixes

* Added additional checks in cost override sensors ([ba41e73](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ba41e7338491b5eceea0780fd343b5106dd16acf))
* Fixed entry already configured error ([6be5ea6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6be5ea6769a3a8f330a5de4892abdf300871e05c))
* Fixed issue where export rates were adjusted during intelligent hours ([df74d13](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/df74d1305a547a88ac7c07230b58a850f24c4528))
* Fixed previous consumption to run calls in parallel ([e621af1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e621af154257ea2285657d16624d025fc292b927))
* Removed tracker tariff potentially looking at wrong API for standing charges ([82fecf1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/82fecf1adde75547b2f9d475291e9bb546dc74ad))


### Features

* Added new sensors and events to expose various rate information ([1e0315e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1e0315e2d585a5d93544dae38b966d15c56b8296))
* Added service to support manually refreshing previous consumption data/costs ([a84a91d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a84a91d96e79bf91520e0329800a8f1372c5a512))

# [8.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.2.1...v8.3.0) (2023-09-23)


### Bug Fixes

* Added service for removing custom external statistics for meters with no active tariff ([2fe1d19](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2fe1d193d71caf23f51c4f74353bb5629e230951))
* **binary-sensor:** Fixed intelligent dispatching sensor not turning on during off peak times ([0901bfd](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0901bfdd4177acba3a09e91228a75f2bf4b7dd69))
* Fixed target rate sensor not restoring state between restarts ([75bcc8f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/75bcc8fffda8534bc61b75f2516e5bbd2a236ddb))
* Raise error on startup if account information is not available, which will cause HA to retry ([4799400](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/47994001c979796eef16dd752d99c36d4ac8136d))


### Features

* Added location data to intelligent dispatches ([4e1a9bd](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4e1a9bd2e1d3903d85fe2d73d8d1567b670a38b4))
* Added support to adjust the day offset for previous consumption sensors beyond the previous day ([062ec3f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/062ec3f66d59e335f30c65d00ab3735f4ebcb7fa))
* **sensor:** Added sensor for indicating if rate is currently off peak ([94a5151](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/94a5151f15fc4c07ccf5243825972ca32bcdd7f3))
* Separated Home mini electricity and gas refresh rates ([6651ebf](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6651ebfe5ebe7ef789aeabfad65c6d81f9f5e345))

# [8.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.1.0...v8.2.0) (2023-08-26)


### Bug Fixes

* Fixed accumulative consumption sensors not starting until 1am ([dd2997b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dd2997b2f85f38d2730c034d32eca43b3ca7a6dd))
* Fixed retrieving standing charges that have no end date ([41b913d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/41b913d3032d3db6ac721567d8a92d71a60a9997))
* Removed unused/undocumented attribute from intelligent dispatching sensor ([56657a2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/56657a23f8c9cfc9f319056d822e9a6d3da6f404))


### Features

* Added repair notification when target rate sensor becomes invalid ([fd52777](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fd527774f1e71185affa0ab7e72d30b674723696))
* **config:** Added more validation around target rates, including around agile tariffs ([8a00c1c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8a00c1c2341550e4e8b5e154ddb6fe4d3c45b5eb))

# [8.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.0.0...v8.1.0) (2023-08-12)


### Bug Fixes

* Added more checks around coordinators ([31205c5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/31205c5037be9ac8a50cc60d3535592263668df5))
* Fixed issue with accumulative cost sensors when used in the energy dashboard ([3db7228](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3db7228ac9d95f501e14abe96e9554a5437bcd44))
* Moved various sensor updates out of update loop and into state property which should stabilize updates ([662a32b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/662a32b8df00484408c2794aefa5d6ff00d2dfa6))
* Removed coordinator setup skipping if already setup ([54bb347](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/54bb347d56f36ad48ecc73a498f22050dc153040))


### Features

* Change order of rates/applicable rates attributes so they're last on rate sensors ([b4d0c6b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b4d0c6b0744312e42a4cd4e2ed86cc6661e8a2dd))
* Updated intelligent dispatching sensor to include vehicle battery size information and charge point power ([b7e0294](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b7e0294675aee0e4d5d5da7a0b7537cbd4443395))
* Updated planned/completed intelligent dispatches to include charge in kwh ([4fec0cf](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4fec0cf2e3dfe9ef95a7dd47a59318725318acf8))

# [8.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.5.2...v8.0.0) (2023-08-05)


### Bug Fixes

* **api-client:** removed tracker fall-back API ([fd095cb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fd095cbc3a06b668c65daf547b220e7d95645ab8))
* Fixed "ignoring invalid device info" error ([c6219d7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c6219d7af3be83d4a44e84f658ba87a6bc818a69))
* **intelligent:** Fixed ready time state when initial value is returned ([8296fce](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8296fce0ab7b156e0be5bcb6131bf6f171177be0))
* Removed empty gas meter devices ([f0c4258](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f0c4258eb28d01b3719bf7bb1671916027d0386f))
* Removed last reset from current demand based on state class warning ([f452ee7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f452ee7665183f8be70ade67c7a6e78d2b2d7876))
* **sensor:** fixed issue with previous rate sensor going unknown when crossing midnight ([45b7e43](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/45b7e43ddd082aeea60cfa7ca681ee2ae9d26ea8))
* **sensors:** Fixed deprecated warning for charge limit sensor ([6b0e894](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6b0e894b9398a2ab079b90717aae865cd66fac15))


### Features

* Added peak/offpeak consumption/cost sensors for current accumlative elec/gas ([e0c756f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e0c756fe57e979a6289f65e7180fe71fb1bebb67))
* Added sensors for current elec/gas accumulative consumption ([d3315a5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d3315a5c86250157e5a242432d0c8935c76598d5))
* Added sensors for current elec/gas accumulative cost ([f6971f3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f6971f3802d4a6840f9b22f77a8545aed0265018))
* Added sensors for current elec/gas accumulative cost ([0dec111](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0dec11124acf00dcc6a887877c3200c05aa7d91c))
* **config:** Added refresh rate configuration for Home Mini ([dbfe805](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dbfe8052df409b9876fb1ac45e4f2ede8eb8ec8c))
* **config:** Improved target rate sensor config to show if an import or export meter is being picked ([e415b41](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e415b4155f43db1bd3fb2134db9fa2535fa3f9a0))
* **sensor:** Added next/previous rate sensors for gas ([dceb784](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dceb78455e7996abc5bff89027fd2b19efeca22c))
* **sensors:** Added functions for retrieving next/previous rates ([79e5471](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/79e5471caa2f61a54b09d90324329362222c4c39))
* **sensor:** updated next/previous electricity sensors to find rates that have a different value to current rate ([37ad6c1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/37ad6c1c82d06dcb4f93fce886ada265258057de))
* **target-rate:** Added ability to invert normal behaviour of target rate sensors when finding target rates ([080d2cc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/080d2cc2c829aaccb805b6b3ed959964aae644e6))
* Updated charges in cost sensors to include raw representation ([e981c27](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e981c2720d6abb561c6b88ca0523d136b38928ab))


### BREAKING CHANGES

* **api-client:** While this shouldn't have a negative effect on anyone, I'm marking the removal of the tracker
fallback API as a breaking change. This is because I believe it's cause bugs to be raised and there
are several threads within the OE forums that don't suggest using it for various reasons
https://forum.octopus.energy/t/finding-the-latest-gas-tracker-api/6021/9. This original tariff that
introduced this work around is now properly supported by the API.
* **sensor:** These sensors no longer look at the next/previous 30 minute rate so behaviour will change for all
tariffs. This is to make them more useful for non agile tariffs. Attributes of these sensors have
also changed. Please review docs for more information.
* **sensor:** The rates attribute on the previous/current/next rate sensors will now contain the previous days
rates. If you are using this attribute, you may need to adjust your use.

## [7.5.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.5.1...v7.5.2) (2023-07-21)


### Bug Fixes

* **sensor:** Fixes to various sensors and how they update their values ([92d8a57](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/92d8a57c5ba65f3ebbb0e9bc92562008f758a3d9))

## [7.5.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.5.0...v7.5.1) (2023-07-20)


### Bug Fixes

* **sensors:** Fixed issue with saving session evaluating incorrectly … ([#317](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/317)) ([66dc168](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/66dc168067fde3363c67809ce90ceb721a34d42f))
* **sensors:** Fixed issue with saving session evaluating incorrectly when data is unavailable ([94a03fb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/94a03fbf53e2b8539982517d66e84eba8ccb6553))

# [7.5.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.4.5...v7.5.0) (2023-07-14)


### Features

* **sensor:** Added various sensors for Octopus Intelligent to support various configurations ([0380377](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/03803772981a812adebe2c6aeb1070192b0e93ba))

## [7.4.5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.4.4...v7.4.5) (2023-07-04)


### Bug Fixes

* Fixed issue with dispatch times and electricity rates ([7a5b470](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7a5b470e542acc616b4fcc3c30e851195feb052a))

## [7.4.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.4.3...v7.4.4) (2023-07-01)


### Bug Fixes

* **api-client:** Fixed  api client to handle graphql errors ([78414d2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/78414d2ddf19afea0f55fda59f702d59feb33347))
* **sensor:** Fixed inclusion of intelligent dispatches in consumption costs and pricings ([34ef0e8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/34ef0e8213a773290db997184d8c4b2815ef7350))
* **sensor:** Fixed issue during BST with rate sensors ([dcfd1b6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dcfd1b62d740469ccd8398a796b7d8d4ca35f623))
* **sensor:** Updated retrieving of rates to try more frequently if rates are out of date ([a50e0bc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a50e0bccd2d75286c2eb9ba7666bbd0068938f37))
* Updated various sensors to update via coordinator callback ([16c1c75](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/16c1c750c2d4705a537ace81b002f7bf8f4707e3))

## [7.4.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.4.2...v7.4.3) (2023-06-16)


### Bug Fixes

* **api_client:** Improved detection of smart meters ([d614210](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d6142108c7e28601f3374c31c288c35c7d8b9f6e))

## [7.4.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.4.1...v7.4.2) (2023-06-04)


### Bug Fixes

* **binary-sensor:** Fixed next_time on target rate sensors to take account of configured offsets ([9673b4e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9673b4ecaa5881a9d2ec3c9f83c2543882b667b5))
* **sensor:** Fixed recovery of electricity rates if new rates fail to be retrieved ([210f6c4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/210f6c4ed6740c03e6147256c1a533c30e00618f))

## [7.4.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.4.0...v7.4.1) (2023-06-03)


### Bug Fixes

* **sensors:** Fixed handling the retrieving of tracker tariff data for non tracker tariffs ([6c277d4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6c277d4bbf26c347418b68604d7efb87c0c4fb49))

# [7.4.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.3.0...v7.4.0) (2023-06-03)


### Bug Fixes

* **config:** Updated mini configuration to have link to minimise confusion ([9d277af](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9d277afeb3a6b8d4bced614ee95ffaeacfb258a5))
* Updated api client to throw errors based on responses and caught appropriately in the coordinators ([c1c031a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c1c031a57587651b3ec34658e224cee75e3e0e17))


### Features

* **sensors:** Updated sensors to appear in disabled state if account info determines no smart meter is present ([b1f123a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b1f123a641defd9abd7fcaf6e6e335dbe575860e))

# [7.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.2.0...v7.3.0) (2023-05-28)


### Features

* **binary-sensor:** Added the ability to force target rate sensors to find the latest applicable set of rates ([dc2e456](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dc2e456e257404c8a29b9444666f6406b3fdec38))

# [7.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.1.3...v7.2.0) (2023-05-21)


### Bug Fixes

* Fixed issue when Octopus Home Mini data can't be retrieved for 1 week or beyond. ([1c05ea7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1c05ea737f5154f75938173bb0e7f93dcba1e859))
* **sensor:** Added missing last reset attribute restoration ([d596b3b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d596b3b005f13bde13096dccf00d4dc3a3bf8309))
* **sensor:** Fixed last_reset of previous electricity consumption/cost ([3996ab7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3996ab7258b02afb157e514384b7c6b5a20db2d0))


### Features

* **sensor:** Added support for comparing previous consumption cost with another tariff ([44ef244](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/44ef244d90192a824b9a21982a760229713aa460))

## [7.1.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.1.2...v7.1.3) (2023-05-13)


### Bug Fixes

* **sensor:** Fixed peak/off peak calculations when off peak cost exceeds peak costs ([317e916](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/317e916602ca005827cdd351ffd67054fcdb620c))

## [7.1.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.1.1...v7.1.2) (2023-05-11)


### Bug Fixes

* **sensor:** Added additional checks around previous consumptions and costs when data is not available ([28b31b5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/28b31b5e4d884d80ede288e5f22c3c69484a2ed1))

## [7.1.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.1.0...v7.1.1) (2023-05-11)


### Bug Fixes

* Added check for when standing charge can't be retrieved ([383ec65](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/383ec6534f4d7dbb500d13bc4e5e22a7c626eb4c))
* Added more checks around retrieving previous rates and consumption ([a1ec6fe](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a1ec6fe139c81532a25ed4048acaef0fcc70127d))

# [7.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.0.0...v7.1.0) (2023-05-11)


### Bug Fixes

* **sensor:** Fixed icon for previous gas consumption sensor ([91f9096](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/91f909636ae02672507708ba2fce4337c9a68e40))
* **sensor:** Fixed rate sensors not having long term statistics ([07db8f8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/07db8f85a1ddd153ce04564aa87195a1dda58be3))


### Features

* **config:** Added detail around target rate hours ([9b084c9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9b084c99601afb7d22ccae27fba7aa287286022a))
* **sensor:** Added disabled sensors for representing electricity peak/off peak consumption and cost for previous day ([76de3fb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/76de3fbfa8cba04a5b7186c1d4702a54b296108b))
* **sensor:** Added min/max/average rates to electricity rate sensors ([df82983](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/df8298350e4ded78c306ba40acdaa89985c4a85f))
* **sensors:** Added support for external statistics for previous consumption sensors (see energy dashboard instructions) ([4d4e460](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4d4e46002b3c8835bea794ba61f44de556554121))

# [7.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.6.1...v7.0.0) (2023-04-18)


### Bug Fixes

* Added check when gas rates are unavailable ([b90131a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b90131a58d9be3011507ae6cac9c3518ae971f43))
* fixed entity names to match documentation and include octopus_energy domain ([f6f589b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f6f589b93990740d236994a08acfdd69cb7a5fad))


### BREAKING CHANGES

* The name of the entity should stay how it was formed when the entities were first created, however
the names might change in either your HA instance or other dependent services.

## [6.6.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.6.0...v6.6.1) (2023-04-10)


### Bug Fixes

* Fixed average cost on target rate sensors to handle when no rates are available ([b67989e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b67989e5e28df55a1bba288b0592d60bee2fb20e))

# [6.6.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.5.0...v6.6.0) (2023-04-08)


### Bug Fixes

* Fixed fallback onto make/model if import/export meter not available ([2940e73](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2940e73361d924bcdcda85f6d7b8fc0993e8cd5e))


### Features

* **binary-sensor:** Added overall average, min and max costs for target rate sensors ([060ea63](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/060ea632a1cb6c66e51c9bd85842dcf39fb1ab3e))

# [6.5.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.4.1...v6.5.0) (2023-04-08)


### Bug Fixes

* **config:** Updated target rate sensor to support type and name to be updated ([4888976](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/48889765161abccaa57497b17fff51f1543635e4))
* Fixed consumption sensors to not be created for users with no smart meters ([34003f4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/34003f400132b7cffa9b930d17520b4282601db0))
* Updated tariff extraction to be more flexible with beta tariffs (e.g V2G) ([3a9c2fb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3a9c2fb98378f7fbb8f0d60e4ab6ded9f26bcfd3))


### Features

* **binary-sensor:** Added cost attributes to target rate sensors ([98c0db9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/98c0db96a418c76707081303b8e67c89d468b70b))
* **sensor:** Updated saving session entity to display current event start/end/duration ([97b49d0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/97b49d03253cc5846ac48a6aee5f011f9614a9ee))
* Update device to include make, model and firmware where available ([f65c34a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f65c34aa524360e8b203e42361adac23ec06a2de))

## [6.4.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.4.0...v6.4.1) (2023-04-01)


### Bug Fixes

* Added more robust checks when retrieving account information ([5898f41](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5898f41b936d453e07c0f66c2c7826096645abe5))
* **api-client:** Added more checks for when meters have no agreements ([ee86fe0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ee86fe0117dd39bc14ad08d4a1f2544f66a0dcd3))

# [6.4.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.3.2...v6.4.0) (2023-04-01)


### Features

* **config:** Added checks for tariffs to report repair errors if not valid ([3f7dc86](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3f7dc86789d6fbfe629f935fc8558094e4e0c510))

## [6.3.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.3.1...v6.3.2) (2023-03-29)


### Bug Fixes

* Added missing requirement for repairs ([69a4bcb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/69a4bcb5af30a8fc91d09fa53c48aa4ff8770702))
* Updated current rate sensors to indicate if prices are capped ([1368349](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/13683499a590fb30fa0afe6fbefd3a91350de519))

## [6.3.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.3.0...v6.3.1) (2023-03-28)


### Bug Fixes

* Handle when account cant be found and display repair message ([7c7801a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7c7801a77f9416dd680580dec66e54de2af712a2))

# [6.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.2.0...v6.3.0) (2023-03-21)


### Bug Fixes

* Updated diagnostics to redact device id ([093fc5a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/093fc5aa1b70110130f1ee8a7063aeb33868731d))


### Features

* Updated account to retrieve tariff product code ([3cdb4b5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3cdb4b5378e3c9175a2d1b8d3f9569aa06c8557c))

# [6.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.1.1...v6.2.0) (2023-03-18)


### Bug Fixes

* **binary-sensor:** Fixed offset incorrectly being applied to target times upon discovery ([94ed934](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/94ed934300d6996601766e5b9f1515df801954d1))


### Features

* **sensor:** Updated names of sensors to not include Octopus Energy ([07fdd8b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/07fdd8b86dec3d92a236f64086cddcdba963919c))

## [6.1.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.1.0...v6.1.1) (2023-03-18)


### Bug Fixes

* **sensor:** Fixed kwh gas sensor device class ([6a25058](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6a2505809a667347f7599dbbed614f4a7636bcd6))

# [6.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.0.1...v6.1.0) (2023-03-18)


### Bug Fixes

* **binary-sensor:** Fixed issue with offset being applied twice for "next_time" in target rate sensors ([d8596fb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d8596fb8ce5c22993d55d6dae426b818639b20a0))


### Features

* **sensor:** Added current consumption for gas through octopus mini ([df7b3dc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/df7b3dc6f13806e6f87d6eb63b98eac1974d5b47))
* **sensor:** Added the ability to configure current gas consumption for octopus mini ([6c6868a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6c6868a5ee54924c47300198d66b4fc149359daf))

## [6.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.0.0...v6.0.1) (2023-03-02)


### Bug Fixes

* **sensor:** Fixed handling of tracker products ([2911ebb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2911ebb43d8126d988f90cda2b1cd2b7409420b0))
* **sensor:** Fixed rate sensors to update on the half hour ([2e2d795](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2e2d79532f48f82bcf6131950be4bd33df7d3139))

# [6.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.4.1...v6.0.0) (2023-02-25)


### Bug Fixes

* **fix(sensor):** Added "export" to export based sensors ([3df28bb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3df28bb298dd31bbad0b226c775f22e886164376))


### Features

* Added option to configure gas calorific value ([d3e3333](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d3e3333c68813face9bff1e89409774e7275eb61))
* Added price cap configuration ([fdd856a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fdd856ac94a8d03649ace52886e485061fd0fde8))
* Added support for home mini ([3f811e3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3f811e3c811ff4471469de1745b3fb83584ff9b2))


### BREAKING CHANGES

* **sensor:** The name of export based electricity sensors have been updated to include the term "export". This is to make it more discoverable for new users.

## [5.4.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.4.0...v5.4.1) (2023-02-07)


### Bug Fixes

* **api-client:** Fixed tracker lookup logic ([c59085a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c59085aefb7afe51ca7ac5f6763969a169e5a614))

# [5.4.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.3.1...v5.4.0) (2023-02-05)


### Bug Fixes

* **sensor:** Fixed restoring attributes from restart ([fdfd72e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fdfd72e5c16f362c5a10a08e4926bcd9d816cc8a))
* **sensor:** Fixed restoring attributes so they're not read only ([bbb3ef8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/bbb3ef840f48dd10aaad670c6999a99ea6c96eeb))


### Features

* **api_client:** Updated rates and standing charge logic to route to tracker endpoint where appropriate ([3be23d0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3be23d075ff36201e89f5ed3ad8aba6eafda330e))

## [5.3.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.3.0...v5.3.1) (2023-01-28)


### Bug Fixes

* **sensor:** Fixed gas rates to work with tracker products ([b2419dc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b2419dc2179a8e54081cd0569d60b2ef19a0165b))

# [5.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.2.1...v5.3.0) (2023-01-20)


### Bug Fixes

* Added more defensive code for account retrieval ([a01513c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a01513c3aac33df3e1f45b4083a4112b6d075999))
* **binary-sensor:** Updated target rates to skip if not enough applicable rates exist for specified period ([e2a2376](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e2a237697df595d5b734aa8b5dc2add5261abfdb))
* **sensor:** Fixed restoring rate sensors to not default to 0. ([85c38cc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/85c38cc7d32f1d6bc586c2416fdb8cf8444649df))


### Features

* **binary-sensor:** Added next duration in minutes for target rates ([bae76b2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/bae76b2bb1703b5849751c4e4cf2649cc1a659e1))
* **binary-sensor:** Added rolling target as attribute ([f1eaac9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f1eaac9bb08b933c091776d908b24749adf99ed1))
* **binary-sensor:** Updated target rate sensors to display how long the current active block is ([2bd037b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2bd037be741d4f4e7d0577e13e0f76798bfb7bdb))
* **sensor:** Added next rate sensor for electricity meters ([8167baf](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8167baf11892609219f02f31b9bf4070c7347d1f))

## [5.2.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.2.0...v5.2.1) (2023-01-16)


### Bug Fixes

* **binary-sensor:** Fixed issues with using update service through automations ([70d101d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/70d101d0709665d2e37b851d25e779ce2d7b2718))

# [5.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.1.0...v5.2.0) (2023-01-15)


### Bug Fixes

* **binary-sensor:** Fixed issue when start/end spans multiple dates ([a4d9550](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a4d9550d9453b476378efc62a2b37857138139b6))
* Removed "export" from name of target rate sensors ([1b22958](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1b229584de5ebf64612d57b36e8e3e1e350cb3f3))


### Features

* Added service for updating target rate config ([4c6a2bb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4c6a2bbd0629ff2628076c8ec11631e69b4d5310))
* **binary-sensor:** Added support for end time being before start time ([8431801](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8431801f5be7519bba6c5ac6ab2cdc2c61c3abad))
* **sensor:** Added new sensor to expose gas as kwh ([d365c45](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d365c4517347059c8b9ed2b4ddff17afb01bcee7))

# [5.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.0.0...v5.1.0) (2022-12-28)


### Bug Fixes

* **sensor:** Added back m3/kWh calculations for gas sensors ([820abde](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/820abde97b05842f64f24e4a85654f68594b3b6f))
* **sensor:** Added last_reset attribute to cost/reading sensors ([2861796](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/286179692651f24308a26d7cb769b27086d3885b))
* **sensor:** Removed SMETS1 configuration as it's no longer used ([eb49841](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/eb498411d3f3f8d18fad573acc196acf7d4cb155))
* **sensor:** Updated min consumption data to be in calculation ([4f55e8d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4f55e8deccd01c22ab743fe6b804daf2345a82e9))


### Features

* **binary-sensor:** Updated next saving session to include end date and duration in minutes ([4d78a00](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4d78a00560eddc5908303495207edaddf606875c))
* **sensor:** Added sensors for current standing charges for electricity and gas ([24641f8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/24641f82847dec5c15a5273099fb9a0ca7d22cc9))
* **sensor:** Updated standing charge to be more specific ([521d9fc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/521d9fcf51736f7ae9e20411d0fdebc46bc07699))

# [5.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.7.1...v5.0.0) (2022-12-17)


### Bug Fixes

* **sensor:** Fixed state class for sensors to "total" ([fda8df6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fda8df6b1b0e7e65cefb7ce245088bc87d10b56b))


### BREAKING CHANGES

* **sensor:** This fix causes long term statistics for the sensors to break. To rectify this, visit https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/108

## [4.7.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.7.0...v4.7.1) (2022-12-08)


### Bug Fixes

* **sensor:** Only set latest date on gas rate sensor if rates are successfully retrieved. ([11f275f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/11f275f63aba585aabb66a9d3c180e35817f0434))

# [4.7.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.6.4...v4.7.0) (2022-12-04)


### Bug Fixes

* **binary-sensor:** Fixed issue with rates mismatch and multiple meters ([1050fd4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1050fd4ab2845db0c76504fedd7df623f552968b))
* **binary-sensor:** Updated target rate sensors to work with export based meters ([0d4757b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0d4757b82dbeaf69bd5d8daedf7c930a00f477db))
* **sensor:** Fixed issue with rates update ([a2fead5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a2fead550b49467863ea1ed533bee5ecbe86deb0))
* **sensor:** Updated sensors to support being restored after reboots ([1f04b14](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1f04b14f7074a7ed7afadcd2faefd3e7288e2c76))


### Features

* **binary-sensor:** Added sensor for when joined saving sessions is active ([93dbd9e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/93dbd9e025c173c62b2ef46d201491a6456940a4))
* **sensor:** Added saving sessions points sensor ([94e465c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/94e465cb1957de719e6ac80a75d75a58e84d625e))

## [4.6.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.6.3...v4.6.4) (2022-10-27)


### Bug Fixes

* Fixed issue with increased debug logging. Also reduced default logging to debug level ([2add166](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2add166b200b89320d5590102ff1a110bcc24fa1))

## [4.6.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.6.2...v4.6.3) (2022-10-26)


### Bug Fixes

* Added additional logging around target rates ([6228020](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/62280200ad3cc1d81f22055c637e81ca219fe15c))

## [4.6.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.6.1...v4.6.2) (2022-10-25)


### Bug Fixes

* **api-client:** Fixed api_client incorrectly absorbing not found requests ([2a96c51](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2a96c515d0d2e7aff2eadf3618edf1fc84a71c09))
* **sensor:** Update rate sensors to report back None if no current rate can be found ([86376ac](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/86376ac1dd9b44b1d499aef8158344943041f891))

## [4.6.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.6.0...v4.6.1) (2022-10-22)


### Bug Fixes

* **config:** Updated rates retrieval to take account of local time ([ccf67ee](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ccf67ee4707055dad2e29f4ab7732d4dd9ce1a95))

# [4.6.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.5.1...v4.6.0) (2022-10-16)


### Bug Fixes

* **binary-sensor:** Fixed issue when sensor is active and calculated on the end date of the last rate ([917f9b5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/917f9b57156dc4ca1c9f381d688d3211a317433a))


### Features

* **api-client:** Moved conversion of rates to 30 minute increments to separate testable function ([412599f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/412599f3a3b37c018d680563c82fdd7cb3cecafa))

## [4.5.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.5.0...v4.5.1) (2022-10-02)


### Bug Fixes

* **binary-sensor:** Fixed text of rolling_target to reflect behaviour ([4840ff3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4840ff36b29139d4ddec047dcd70fa959f1247cb))
* **config:** Fixed issue with configuring when star/end/offset not set ([4916f68](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4916f6852b2ba2aeafa5fba2814b6986f0257400))
* **config:** Fixed loading binary sensor when start/end is not set ([dcafda4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dcafda4e239f443051685b2773943a5f9ca3e0a8))

# [4.5.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.4.0...v4.5.0) (2022-10-01)


### Bug Fixes

* **binary-sensor:** Fixed issue when start/end time isn't set ([7ab9b2d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7ab9b2dff3220ce060db51d321fac4f6edafda8f))
* Fixed day/night times for economy 7 tariffs when using a smart meter. Thanks [@696](https://github.com/696)GrocuttT  ([c860a8a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c860a8a3eaaf0ca1a03059d1be87e51d4cc36831))
* Updated consumption sensors to wait for more than 2 charges to be present ([aa97647](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/aa97647ae407ddb75bc0c0fa2ccdb878f55ab47e))


### Features

* **binary-sensor:** Added facility to restrict target rates sensors from only reaching the target once a day ([67d2993](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/67d299354fd16dc7303837e292ed3aa73f5ea645))

# [4.4.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.3.0...v4.4.0) (2022-07-23)


### Features

* **device:** Added debug logging for account information (not redacted) ([576c93d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/576c93d5e9d589e53140866a74cca27f22626fc4))
* **device:** Added support to download diagnostics which includes redacted account information ([01fdf4e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/01fdf4e1b68822461813c719bb7756c12e9aabcb))

# [4.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.2.1...v4.3.0) (2022-07-04)


### Bug Fixes

* **api-client:** Updated get_account to use graphql so that inactive meters are ignored ([f05dcd9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f05dcd9e326c11c4e82ada503d9aceb2841b5738))
* **sensor:** Fixed gas sensor ([975f4fe](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/975f4fe1c03648b6cca44ae63480a739cafd7ebf))
* Updated translations to not include title as not needed ([43d1a0e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/43d1a0e5e2df6391418a557b4228bf1a379d80ee))


### Features

* **sensor:** Added rate information to current electricity rate sensor ([cfb4043](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/cfb40433a5aa002944b6e16650a10499e57611b0))
* **sensor:** Updated electricity and gas sensors to be associated with devices ([38d8adb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/38d8adb18a5ca8d6ba0f0cd14fcea9bf14ea917b))

## [4.2.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.2.0...v4.2.1) (2022-06-18)


### Bug Fixes

* Fixed incorrect logging for debugging entries ([d5fad1d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d5fad1dbcd182e184063281152f2cb2b98aed49a))
* **sensor:** Fixed issue where gas consumption was being incorrectly calculated for SMETS1 sensors ([065ec88](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/065ec88df8758738bae41a14bb5b309968e956a0))

# [4.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.1.3...v4.2.0) (2022-05-07)


### Features

* **binary_sensor:** Updated target rate sensors to be updatable ([a6fbcca](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a6fbccad237c3d9d2294ba11a7e8029e78cb0bdb))
* **binary-sensor:** Added ability to apply offsets to target rate sensors ([faafa1b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/faafa1bdbe3434d571bc56761ff0efc9b3f58adc))
* **sensor:** Moved targeting sensor update logic to external functions ([74908e1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/74908e1f9bc06284178bbfba304be777bd54259d))
* **sensor:** Updated sensor icons to be gbp instead of usd ([66dfc54](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/66dfc54a0e8b745472b7f24a4995fed89f028e94))

## [4.1.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.1.2...v4.1.3) (2022-03-23)


### Bug Fixes

* **sensor:** Fixed issue where active agreement was not being found, causing sensors to not appear ([85acdac](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/85acdacf7ba50bb65cd8512f14c1d4a118a11dfa))

## [4.1.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.1.1...v4.1.2) (2022-03-22)


### Bug Fixes

* **sensor:** More fixes to sensor logging. ([b0c4213](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b0c4213be7372480a7aef260d7fe711e15156211))

## [4.1.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.1.0...v4.1.1) (2022-03-22)


### Bug Fixes

* **sensor:** Fixed log when no active agreement present ([75af243](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/75af2439988c4090439c598b397db139f1e0132c))

# [4.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.0.0...v4.1.0) (2022-03-22)


### Features

* **sensor:** added info logs to indicate why sensors aren't added ([cc3fbeb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/cc3fbebf413ef18397f604536f867af71a0205a2))

# [4.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v3.1.0...v4.0.0) (2022-03-07)


### Bug Fixes

* Fixed support for meters that both import and export electricity (Thanks [@696](https://github.com/696)GrocuttT) ([1391dc8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1391dc83fc23000d434dda70ea8fdd802721ef59))


### Features

* **config:** Updated selecting target meters for target sensors to be more user friendly ([b1dc00f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b1dc00f49db4a225de2c66317a1e9b45800dc145))
* **sensor:** Added tariff code to electricity and gas consumption sensors ([a728652](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a72865291a18e3d9cb38ecfa3ae7455b4339d216))
* **sensor:** Updated electricity sensors to include is_export attribute ([d35967e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d35967ed0b51474b4d23111f038bd613147b5e41))
* **sensor:** updated gas sensors to include mprn in name ([af528ef](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/af528efa98d99e46675f83fbc7214b960fbf474f))
* **sensor:** Updated previous gas consumption to display kwh and m3 values in attributes ([745c51f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/745c51f1c92e312b6cf55f8583acc36cccfd8700))


### BREAKING CHANGES

* **sensor:** This has been updated for consistency with the electricity sensor changes
* Unfortunately in order to support import/exports, electricity sensors now include both the mpan and serial number in their name. This means you will need to update any automations or dashboards that rely on these sensors.

# [3.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v3.0.4...v3.1.0) (2022-01-15)


### Bug Fixes

* **sensors:** Fixed current gas rate period to be for the day ([7a62150](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7a62150881f326904e181366f611614a01fcc31b))


### Features

* **sensor:** added current gas rate sensor ([ecfe774](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ecfe774190da1d6c80e969f7a024d29242add2aa))

## [3.0.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v3.0.3...v3.0.4) (2022-01-01)


### Bug Fixes

* **sensor:** Updated consumption to not require 48 entries ([9bd6790](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9bd6790f05c4fd6bf1a44cbe0cf9433f00050d3d))
* **sensor:** Updated sensors to not require 48 entries for consumption ([15fd45c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/15fd45c8df2f0b1964af13b34a5cd125c481dd07))

## [3.0.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v3.0.2...v3.0.3) (2022-01-01)


### Bug Fixes

* **api-client:** fixed retrieving rates for agile and go tariffs ([9a12ac5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9a12ac506ee5f9d4f9de71082e5ebd0ba4658d28))
* **api-client:** updated to treat server errors as not receiving any data ([c111463](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c11146311a72bdf05bb555082fb27ad1e784c434))

## [3.0.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v3.0.1...v3.0.2) (2021-12-28)


### Bug Fixes

* **api-client:** Added additional logging for failing to read json response ([fa3b33d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fa3b33de7990c53842d9fd862af5be860028a7b2))
* **sensor:** Added more logging around failing to retrieve consumption rate. ([dbec7a5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dbec7a5fc88b157ee01288bd09b1787b3dd8f02e))

## [3.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v3.0.0...v3.0.1) (2021-12-23)


### Bug Fixes

* **sensor:** updated tariff code in sensor setup to be retrieved after it's been setup in the rate coordinator ([9caade9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9caade91eac4ff14a785bc4d5c1ec455ec047bba))

# [3.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v2.0.0...v3.0.0) (2021-12-22)


### Bug Fixes

* **sensor:** Removed code for falling back on fixed tariffs if no agreement is found ([9a5045b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9a5045bca5746e6fb289dda1616f795716e9fad1))


### Features

* **sensor:** Added sensors for accumulative cost of gas for the previous day ([42a1408](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/42a140827a4fc03694a5cc2d1fcaea31010003b5))
* **sensor:** Created coordinator for retrieving current reading and created initial electricity consumption cost ([4f09269](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4f092694a7a53040b2364ffb6cc74cbf8a6cff57))
* **sensor:** removed current consumption sensors due to insufficient data provided by Octopus Energy ([0470ff3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0470ff38c88f1bc480bbe949fed05f4bf16bf57b))
* **sensor:** Removed registering of current consumption sensors ([d263a68](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d263a6889d907506c6f797329e18c7ac14377b75))
* **sensor:** Updated previous day consumption to only be valid if enough data points are available ([9e71ef2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9e71ef28481cd5074ae0a1c4281c4e4166d87d0e))
* **sensor:** Updated previous day cost sensor to include breakdown and standing charges ([6618246](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/66182462a8d23cde7ce745ddfcb3543e7920fe68))
* updated docs ([dff4d16](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dff4d16895025799364fd0ab00815c95e87150d8))


### BREAKING CHANGES

* We no longer fall back to fixed rate agreements if an active agreement can't be found. This was
added by mistake when people were not receiving sensors when they had moved home and therefore an
inactive house was being picked up. This means that some sensors may disapper, but these should just
be inactive meters.
* **sensor:** Latest consumption sensors are no longer available, which may cause issues anywhere they are used.

# [2.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v1.2.0...v2.0.0) (2021-11-10)


### Bug Fixes

* **api-client:** fixed get_account to find the first property that hasn't been moved out of ([970a7a5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/970a7a58bdb00504b2c922d6e0a4632e71d9a17f))


### BREAKING CHANGES

* **api-client:** This change could cause the sensors associated with your meters to change, as they may have been
associated with a property you had moved out of

# [1.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v1.1.0...v1.2.0) (2021-10-30)


### Bug Fixes

* Updated how we determine if we're on an expired fixed tariff ([075766f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/075766f3ece1a021c889ab0032cd807c028e9300))


### Features

* Updated to move to variable tariffs if a meter's latest agreement was fixed term ([37ee143](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/37ee143737458ec3ead08d43bfb6b2cfed8680cc))
