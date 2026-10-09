---
title: "Territories: the EU VAT area and DHL territory codes"
---

These rules decide which recipients count as outside the EU VAT area and which country code each advisory reads.
The plugin decides membership from its own territory table, independent of karrio's `EUCountry`, which lists Greece as `EL` and lacks `AX` and `XI`.
The full table and every determination on this page are specified in the [specification](../../openspec/specs/plugins/advisor-nordic-conventions/spec.md); the same table and normalisation are applied by the PostNord and DHL Freight Sweden connectors, and a test in this repository checks the parity.

## The EU VAT area

The table matches Tullverket's list of EU customs and fiscal territories as it applies to goods movements.
The EU member states with Greece as `GR` are inside, Monaco is inside, and Northern Ireland is inside, identified as `GB` with a postal code beginning `BT`; Monaco's French-style postal codes 98000-98099 keep their inside verdict through the `FR` country code, so only the `MC` country code changes verdict.
Northern Ireland's inside verdict is the goods-movement verdict: Northern Ireland is inside the EU VAT area for goods and outside it for services, and the plugin decides customs-document advice for goods shipments.
Great Britain other than Northern Ireland is outside.

An address in one of the ranges below is outside, whatever the member-state country code says.

| Country | Postal codes | Territory |
|---------|--------------|-----------|
| FI | 22000-22999, or `AX` | Åland |
| ES | 35000-35999, 38000-38999, or `IC` | Canary Islands |
| ES | 51000-51999, 52000-52999, or `EA` | Ceuta, Melilla |
| DE | 78266, 27498 | Büsingen, Heligoland |
| GR, EL | 63086 | Mount Athos |
| IT | 23041, 22061 | Livigno, Campione d'Italia |
| FR | 97000-97999, or `GP`, `GF`, `MQ`, `RE`, `YT` | French overseas departments |
| FR | 98600-98899 | Wallis and Futuna, French Polynesia, New Caledonia |
| DK | 3800-3999, or `FO`, `GL` | Faroe Islands, Greenland |

The `DK` range is the one DHL Freight Sweden's product manual v5.26 gives for "Greenland & The Faroe Islands"; the two `FR` ranges are the operator's, inside the manual's delivery exclusion 97100-99999, which also covers Monaco's 98000 and is therefore not adopted.

## Postal-code normalisation

A postal code is upper-cased and trimmed, loses a leading prefix code together with the hyphen and whitespace after it, and is then compared after removing spaces.
A prefix code is the address's own country code, or a territory code with numeric postcodes whose parent is that country (`AX` under `FI`, `FO` and `GL` under `DK`, `IC` and `EA` under `ES`), followed by a hyphen, whitespace, or a digit; `GB` is a prefix code only when a hyphen or whitespace follows it, and `JE`, `GY`, `IM`, and `BT` are never prefix codes.
The DHL Freight Sweden connector applies the same normalisation.

Under `DK`, an address is outside when the prefix code removed from its postal code is `FO` or `GL`, whatever number follows, or when its normalised postal code is exactly three digits, the Faroese format, because the Faroe Islands and Greenland are outside the EU VAT area; a four-digit `DK` postal code outside 3800-3999 stays inside.
A postal code that is not purely numeric after this normalisation leaves the country-level decision unchanged, except that the Northern Ireland prefix comparison applies to a normalised postal code beginning `BT` whether or not it is purely numeric.

## DHL territory codes

For a `dhl_freight_sweden` shipment the plugin reads the shipper's and the recipient's country codes as the DHL Freight Sweden connector books them, replacing a territory code by its parent country before the scope and EU VAT area checks and in every DHL Freight Sweden advisory that reads a country.

| Territory | Code | Read as |
|-----------|------|---------|
| Åland | AX | FI |
| Faroe Islands | FO | DK |
| Greenland | GL | DK |
| Canary Islands | IC | ES |
| Ceuta, Melilla | EA | ES |
| Jersey | JE | GB |
| Guernsey | GG | GB |
| Isle of Man | IM | GB |
| Northern Ireland | XI | GB |

The postal code is used as given; the EU VAT area table is unchanged, and only the country code it is asked about changes.
So `XI` with a `BT` postcode is inside the EU VAT area, `XI` without one is treated as Great Britain outside it, and Jersey, Guernsey, and the Isle of Man receive the Great Britain advice.
The mapping is the connector's `TERRITORY_PARENTS` table in `karrio/providers/dhl_freight_sweden/units.py`, copied into the plugin's `karrio/plugins/advisor_nordic_conventions/territories.py` and checked against the connector by a test that runs when the connector is importable.
For other carriers the plugin reads the country codes as given: a PostNord shipment to `XI` with a `BT` postcode has recipient country `XI`, outside the EU VAT area.

## Territory postal codes

A DHL Freight Sweden recipient that carries the country code `AX`, `IC`, `EA`, `FO`, or `GL` must carry a postal code of its territory, because such a code is otherwise booked as the parent's mainland.
The plugin returns [Territory postal code](advisories.md#advisor_nordic_conventions_dhl_freight_sweden_territory_postal_code_mismatch) at level `warning` when that postal code is missing or, normalised under the parent country as above, lies outside the territory, and returns it whether or not the recipient, read under its parent country, lies outside the EU VAT area.

| Code | Territory | Postal codes |
|------|-----------|--------------|
| AX | Åland | FI 22000-22999 |
| IC | Canary Islands | ES 35000-35999, 38000-38999 |
| EA | Ceuta, Melilla | ES 51000-51999, 52000-52999 |
| FO | Faroe Islands | DK 3800-3999, or a three-digit code |
| GL | Greenland | DK 3800-3999 |

The Faroe rule is the broadest: a three-digit postal code is the Faroese format, so `FO` with postal code 100 lies inside its territory while `AX` with the mainland code 00100 lies outside its own.
`JE`, `GG`, `IM`, and `XI` have no range and are not checked.
The connector refuses the booking with `TerritoryPostalCodeError` when the check fails, and the territories and their postal codes are the connector's `TERRITORY_POSTAL_CODES`, copied into the plugin and checked against the connector by a test that runs when the connector is importable.
