# Spec Delta

## RENAMED Requirements

### Requirement: The EU VAT area follows the connectors' definition

- FROM: `### Requirement: The EU VAT area follows the connectors' definition`
- TO: `### Requirement: The EU VAT area follows Tullverket for goods`

## MODIFIED Requirements

### Requirement: The EU VAT area follows Tullverket for goods

The plugin SHALL decide EU VAT area membership from its own territory table, independent of karrio's `EUCountry`, which lists Greece as `EL` and lacks `AX` and `XI` (FN:235, FN:276, S).
The table SHALL match Tullverket's list of EU customs and fiscal territories as it applies to goods movements (FN:58-65, W): the EU member states with Greece as `GR` are inside; Monaco is inside (FN:64, W); Northern Ireland is inside, identified as `GB` with a postal code beginning `BT` (FN:64, W); and Åland (`AX`, or `FI` 22000-22999), the Canary Islands (`IC`, or `ES` 35000-35999 and 38000-38999), Ceuta (`ES` 51000-51999), Melilla (`ES` 52000-52999), Büsingen (`DE` 78266), Heligoland (`DE` 27498), Livigno (`IT` 23041), Campione d'Italia (`IT` 22061), the French overseas departments (`GP`, `GF`, `MQ`, `RE`, `YT`), and Mount Athos (`GR` 63086) are outside.
Great Britain other than Northern Ireland is outside (FN:65, W).
Northern Ireland's inside verdict is the goods-movement verdict: Northern Ireland is inside the EU VAT area for goods and outside it for services, and the plugin decides customs-document advice for goods shipments, so the territory table carries no services verdict.
Monaco's French-style postal codes 98000-98999 keep their inside verdict through the `FR` country code, so only the `MC` country code changes verdict.
Postal codes SHALL be compared after removing spaces, and a postal code that is not purely numeric SHALL leave the country-level decision unchanged, except that the Northern Ireland prefix comparison SHALL apply to a postal code beginning `BT` whether or not the postal code is purely numeric.

#### Scenario: Åland by postal code is outside

- **WHEN** a PostNord shipment is created from Sweden to `FI` with postal code 22100
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply

#### Scenario: Greece is inside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `GR`
- **THEN** the plugin returns no message

#### Scenario: Canary Islands by postal code are outside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `ES` with postal code 35 001
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: Mount Athos by postal code is outside

- **WHEN** a PostNord shipment is created from Sweden to `GR` with postal code 630 86
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply

#### Scenario: Monaco by country code is inside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `MC` with postal code 98000
- **THEN** the plugin returns no message

#### Scenario: Monaco by French postal code is inside

- **WHEN** a PostNord shipment is created from Sweden to `FR` with postal code 98000
- **THEN** the plugin returns no message

#### Scenario: Northern Ireland is inside for goods

- **WHEN** a PostNord shipment is created from Sweden to `GB` with postal code BT1 1AA
- **THEN** the plugin returns no message

#### Scenario: Great Britain outside Northern Ireland is outside

- **WHEN** a PostNord shipment is created from Sweden to `GB` with postal code EC1A 1BB
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply
