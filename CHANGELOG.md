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
