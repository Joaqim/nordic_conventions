"""Advisory codes of the Nordic conventions plugin.

Every advisory code value is the plugin identity nordic_conventions_, matching
PLUGIN_ID, the package name, and the karrio.plugins entry-point name, followed
by scope and topic segments, all lower_snake_case.
Codes are consumer-facing API surface, so renaming one is a breaking change.
"""

import enum


class AdvisoryClassification(str, enum.Enum):
    postnord_se_no_digital_invoice = "nordic_conventions_postnord_se_no_digital_invoice"
    postnord_se_postpaket_commercial_invoice = "nordic_conventions_postnord_se_postpaket_commercial_invoice"
    postnord_se_export_paper_invoice = "nordic_conventions_postnord_se_export_paper_invoice"
    postnord_fi_export_invoice = "nordic_conventions_postnord_fi_export_invoice"
    postnord_dk_export_documents = "nordic_conventions_postnord_dk_export_documents"
    dhl_freight_sweden_customs_mode_missing = "nordic_conventions_dhl_freight_sweden_customs_mode_missing"
    dhl_freight_sweden_invoice_copy = "nordic_conventions_dhl_freight_sweden_invoice_copy"
    dhl_freight_sweden_attached_documents = "nordic_conventions_dhl_freight_sweden_attached_documents"
    dhl_freight_sweden_voec_marking = "nordic_conventions_dhl_freight_sweden_voec_marking"
    invoice_type_content_mismatch = "nordic_conventions_invoice_type_content_mismatch"
    attestation_conflict = "nordic_conventions_attestation_conflict"
