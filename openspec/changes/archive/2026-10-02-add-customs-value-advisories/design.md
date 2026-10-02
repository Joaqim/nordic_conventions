# Design

## Rule placement

The Switzerland discount and the zero-value rules apply across carriers, so they live in a new `rules/customs_values.py`; the two Parcel Connect rules are DHL Freight Sweden specific and join `rules/dhl_freight_sweden.py`.
All four read the lane through `lanes.lane_of`, so they advise only at shipment creation, only for the shippers and carriers in scope, and only outside the EU VAT area.

## Triggers

A commodity is discounted when its `metadata` carries a `discount_percentage` that is not none, or when its `value_amount` is 0 or none.
A zero-valued commodity is one whose `value_amount` is 0 or none, because the PostNord connector sends both without a value element (karrio fork `modules/connectors/postnord/karrio/providers/postnord/shipment/create.py:349-355` at 7bb7f0f79, S).
`details.lines` lists zero-based commodity indexes, so a consumer can point at the line.
The product manual's country lists give two different reasons, so they are two classifications with their own messages.
`nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` fires where a product does not serve the destination: 109, 112, or 107 to Switzerland, and 107 to Great Britain.
`nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement` fires for 109 or 112 to Great Britain, which these products serve only by separate agreement with DHL.
`NOT_SERVED` maps each destination to the products that do not serve it and the message stating so, so a further destination is one entry.

## Room to suppress the Great Britain advisory

A consumer holding the separate agreement may later want `nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement` suppressed.
The attestation mechanism already provides the shape: `with_attestations` omits an advisory whose non-empty answering set is covered by the request's effective attestations.
Adding a `Procedure` member for the agreement and mapping `nordic_conventions_dhl_freight_sweden_parcel_connect_gb_agreement` to it in `ANSWERING` would let that consumer set the option key to true, with no change to the rule or the wrapper, and would leave `nordic_conventions_dhl_freight_sweden_parcel_connect_not_served` unanswerable.
This change adds no such procedure and maps the code to the empty set.

## The VOEC split is a README note, not a rule

Skatteetaten's VOEC guidelines (March 2024) prohibit splitting goods sold as one unit into separate consignments to stay under the NOK 3 000 limit.
A rule cannot detect that reliably: `lanes.lane_of` reduces one `ShipmentRequest` to a lane (`lanes.py:137-185`); karrio runs every advisor on a deep copy of one request (`karrio/core/advisors.py:85-116` at 7bb7f0f79); `AdvisorContext` carries only carrier identity, test mode, the operation, and connection config (`advisors.py:27-52`); and neither `ShipmentRequest` nor `Commodity` records which goods were sold as one unit or which other consignments belong to the same sale.
The README therefore states the prohibition with its source in Non-goals.

## Citation correction

`PNS` (`openspec/specs/postnord/customs-declaration/spec.md` at 60312fe2e) remains the cited specification, and its footnote is unchanged.
The parcel customs invoice it specifies was implemented on the fork branch `feat-postnord-customs-invoice` (tip face88f37) and entered develop through merge 52d21fbfb; `PNS_PARCEL_CUSTOMS_INVOICE` now names that implementation in its reference, and `sources.py` and the main specification's purpose say so.

## Sources

Each new source is tagged W with its verbatim or paraphrased statement as recorded in the consumer's verified research of 2026-10-02; the Swiss statement is a paraphrase of the German text, flagged by its wording.
