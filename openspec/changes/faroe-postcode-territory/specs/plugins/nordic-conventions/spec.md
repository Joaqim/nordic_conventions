# Spec Delta

## MODIFIED Requirements

### Requirement: The EU VAT area follows Tullverket for goods

The plugin SHALL decide EU VAT area membership from its own territory table, independent of karrio's `EUCountry`, which lists Greece as `EL` and lacks `AX` and `XI` (FN:235, FN:276, S).
The table SHALL match Tullverket's list of EU customs and fiscal territories as it applies to goods movements (FN:58-65, W): the EU member states with Greece as `GR` are inside; Monaco is inside (FN:64, W); Northern Ireland is inside, identified as `GB` with a postal code beginning `BT` (FN:64, W); and Åland (`AX`, or `FI` 22000-22999), the Canary Islands (`IC`, or `ES` 35000-35999 and 38000-38999), Ceuta (`ES` 51000-51999), Melilla (`ES` 52000-52999), Büsingen (`DE` 78266), Heligoland (`DE` 27498), Livigno (`IT` 23041), Campione d'Italia (`IT` 22061), the French overseas departments (`GP`, `GF`, `MQ`, `RE`, `YT`, or `FR` 97000-97999), Wallis and Futuna, French Polynesia, and New Caledonia addressed under `FR` (`FR` 98600-98899), the Faroe Islands and Greenland addressed under `DK` (`DK` 3800-3999), and Mount Athos (`GR` or `EL` 63086) are outside.
The `DK` range is the one DHL Freight Sweden's product manual v5.26 gives for "Greenland & The Faroe Islands" (W, MAN v5.26 §5.3 p.18, §5.14 p.63, §5.15 p.66); the two `FR` ranges are the operator's, inside the manual's delivery exclusion 97100-99999, which also covers Monaco's 98000 and is therefore not adopted.
Great Britain other than Northern Ireland is outside (FN:65, W).
Northern Ireland's inside verdict is the goods-movement verdict: Northern Ireland is inside the EU VAT area for goods and outside it for services, and the plugin decides customs-document advice for goods shipments, so the territory table carries no services verdict.
Monaco's French-style postal codes 98000-98099 keep their inside verdict through the `FR` country code, so only the `MC` country code changes verdict.
A postal code SHALL be upper-cased and trimmed, SHALL lose a leading prefix code together with the hyphen and whitespace after it, and SHALL then be compared after removing spaces.
A prefix code is the address's own country code, or a territory code with numeric postcodes whose parent is that country (`AX` under `FI`, `FO` and `GL` under `DK`, `IC` and `EA` under `ES`), followed by a hyphen, whitespace, or a digit; `GB` is a prefix code only when a hyphen or whitespace follows it, and `JE`, `GY`, `IM`, and `BT` are never prefix codes.
The DHL Freight Sweden connector applies the same normalisation.
Under `DK`, an address SHALL be outside when the prefix code removed from its postal code is `FO` or `GL`, whatever number follows, or when its normalised postal code is exactly three digits, the Faroese format, because the Faroe Islands and Greenland are outside the EU VAT area (FN:63, W); a four-digit `DK` postal code outside 3800-3999 stays inside.
A postal code that is not purely numeric after this normalisation SHALL leave the country-level decision unchanged, except that the Northern Ireland prefix comparison SHALL apply to a normalised postal code beginning `BT` whether or not it is purely numeric.

#### Scenario: Åland by postal code is outside

- **WHEN** a PostNord shipment is created from Sweden to `FI` with postal code 22100
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply

#### Scenario: Åland by country-prefixed postal code is outside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `FI` with postal code `FI-22100`, `fi 22100`, `FI22100`, or `FI 22 100`
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: Åland by territory-prefixed postal code is outside

- **WHEN** a PostNord shipment is created from Sweden to `FI` with postal code `AX-22100`
- **THEN** the recipient is treated as outside the EU VAT area, because `AX` is a territory code whose parent is `FI`

#### Scenario: Letters that begin a postal code are kept

- **WHEN** a PostNord shipment is created from Sweden to `MT` with postal code `MTF 1234`
- **THEN** the recipient is treated as inside the EU VAT area

#### Scenario: Greece is inside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `GR`
- **THEN** the plugin returns no message

#### Scenario: Canary Islands by postal code are outside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `ES` with postal code 35 001
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: French overseas department by postal code is outside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `FR` with postal code 97400
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: French Pacific collectivity by postal code is outside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `FR` with postal code 98713
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: Faroe Islands and Greenland by Danish postal code are outside

- **WHEN** a PostNord shipment is created from Sweden to `DK` with postal code `DK 3800` or `DK-3900`
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply

#### Scenario: Faroe Islands and Greenland by territory-prefixed Danish postal code are outside

- **WHEN** a PostNord shipment is created from Sweden to `DK` with postal code `FO-100`, `fo 100`, `FO100`, or `GL 3900`
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: Faroese three-digit postal code under Denmark is outside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `DK` with postal code 100 or `DK-100`
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: Danish four-digit postal code outside the Faroe and Greenland range is inside

- **WHEN** a PostNord shipment is created from Sweden to `DK` with postal code 1000 or `DK-2100`
- **THEN** the recipient is treated as inside the EU VAT area

#### Scenario: Mount Athos by postal code is outside

- **WHEN** a PostNord shipment is created from Sweden to `GR` or `EL` with postal code 630 86
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply

#### Scenario: Monaco by country code is inside

- **WHEN** a DHL Freight Sweden shipment is created from Sweden to `MC` with postal code 98000
- **THEN** the plugin returns no message

#### Scenario: Monaco by French postal code is inside

- **WHEN** a PostNord shipment is created from Sweden to `FR` with postal code 98000
- **THEN** the plugin returns no message

#### Scenario: Northern Ireland is inside for goods

- **WHEN** a PostNord shipment is created from Sweden to `GB` with postal code BT1 1AA or `GB-BT1 1AA`
- **THEN** the plugin returns no message

#### Scenario: Channel Islands and Isle of Man postcodes are not prefixes

- **WHEN** a PostNord shipment is created from Sweden to `GB` with postal code JE2 3AB, GY1 1AA, or IM1 1AA
- **THEN** the recipient is treated as outside the EU VAT area

#### Scenario: Great Britain outside Northern Ireland is outside

- **WHEN** a PostNord shipment is created from Sweden to `GB` with postal code EC1A 1BB
- **THEN** the recipient is treated as outside the EU VAT area and the Swedish PostNord advisories for destinations outside the EU VAT area apply
