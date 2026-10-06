import logging

import attr
import karrio.core.metadata as metadata

import karrio.plugins.advisor_nordic_conventions.attestations as attestations
import karrio.plugins.advisor_nordic_conventions.procedures as procedures
from karrio.plugins.advisor_nordic_conventions.procedures import Procedure, expected_procedures

ADVISORS = [
    attestations.with_attestations(rule) for rule in procedures.RULES
] + [attestations.attestation_conflicts]

# The stdlib logger is used because karrio.core.utils.logger is not
# guaranteed on karrio versions that predate the advisors hook.
HOOK_AVAILABLE = "shipment_advisors" in attr.fields_dict(metadata.PluginMetadata)

if not HOOK_AVAILABLE:
    logging.getLogger(__name__).warning(
        "karrio shipment advisors hook unavailable; advisor_nordic_conventions registers no advisors"
    )

METADATA = metadata.PluginMetadata(
    id="advisor_nordic_conventions",
    label="Nordic Conventions",
    description=(
        "Trade-document advisories for PostNord and DHL Freight Sweden shipments "
        "from Sweden, Denmark, and Finland to destinations outside the EU VAT area"
    ),
    status="beta",
    **(dict(shipment_advisors=ADVISORS) if HOOK_AVAILABLE else {}),
)
