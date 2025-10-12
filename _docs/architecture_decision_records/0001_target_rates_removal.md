# 0001 - Deprecation and removal of Target Rate Sensors in Octopus Energy Integration

## Status
Accepted

## Context
Target rate sensors are currently a core feature of the Octopus Energy integration. A variation of this feature was also introduced into the [Carbon Intensity integration](https://github.com/BottlecapDave/HomeAssistant-CarbonIntensity), where carbon emissions were used instead of price.  

Maintaining this feature across multiple integrations has become problematic, as it requires ongoing effort to ensure feature parity. Meanwhile, more energy providers are emerging with dynamic pricing models similar to Octopus Energy that cannot benefit from the existing implementation.  

In addition, there are broader automation opportunities beyond energy pricing, such as identifying optimal times for solar generation, that could leverage this functionality.  

To address these issues, a new integration, [Target Timeframes](https://bottlecapdave.github.io/HomeAssistant-TargetTimeframes/), has been developed. It abstracts the concept of selecting optimal timeframes from the data source, allowing it to work with any metric (price, carbon intensity, generation, etc.). This ensures long-term viability and avoids duplication of effort across multiple integrations.

## Decision
Deprecate and remove target rate sensors from the Octopus Energy integration in favor of the Target Timeframes integration.

- A migration guide has been provided: [Target Timeframes Migration Guide](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/migrations/target_timeframes/).  
- A set of [blueprints](https://bottlecapdave.github.io/HomeAssistant-TargetTimeframes/blueprints/#octopus-energy) for using Octopus Energy data with Target Timeframes is already available.  
- A repair notice has been introduced to inform users of the upcoming removal.  
- The target rate sensors feature will be removed six months from the notice, around the end of **November 2025**.  

The Carbon Intensity integration has already removed its variation due to a smaller user base. Given the higher user count of Octopus Energy, this proposal is being [made openly](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/discussions/1305) before proceeding.

## Consequences

### Positive
- Centralizes the feature into a single integration, reducing maintenance overhead.  
- Ensures consistent functionality and feature parity across different use cases.  
- Provides flexibility for multiple data sources beyond Octopus Energy (dynamic pricing, carbon intensity, solar generation, etc.).  
- Protects users from losing the feature if they move away from Octopus Energy.  

### Negative
- Users will need to migrate their automations to the Target Timeframes integration.  
- Some short-term disruption may occur as users adapt to the new integration.  
- Potential gaps in the new integration’s functionality may need to be identified and addressed through community feedback.  
