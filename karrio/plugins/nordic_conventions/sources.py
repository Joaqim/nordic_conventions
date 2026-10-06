"""Sources cited by the Nordic conventions advisories.

Each ``Source`` carries the evidence tag of the karrio fork's facts note
``docs/notes/customs/nordic-trade-documents-facts.md`` (branch
``docs-openspec``, commit baf8eb3dd), cited as FN with line numbers: S is
repository code or vendored specification, W is public carrier or authority
documentation, and I is inference. PNS and DFS are the karrio fork's main
specs ``openspec/specs/postnord/customs-declaration/spec.md`` and
``openspec/specs/dhl-freight-sweden/customs/spec.md`` on branch
``docs-openspec`` at commit 60312fe2e. The parcel customs invoice that PNS
specifies entered the connector on branch ``feat-postnord-customs-invoice``
(tip face88f37), merged into the fork's develop by 52d21fbfb.
"""

import typing

import attr

EVIDENCE_TAGS = ("S", "W", "I")

FACTS_NOTE = "karrio fork docs/notes/customs/nordic-trade-documents-facts.md@baf8eb3dd"
PNS = "karrio fork openspec/specs/postnord/customs-declaration/spec.md@60312fe2e"
DFS = "karrio fork openspec/specs/dhl-freight-sweden/customs/spec.md@60312fe2e"

PN_SE_EN_PAGE = "https://web.archive.org/web/20260116090151/https://www.postnord.se/en/business/import-export-customs/customs-documents-and-shipping-documents/"
PN_SE_SV_PAGE = "https://www.postnord.se/foretag/import-export-tull/tulldokument-och-frakthandlingar-for-foretag/ (Wayback 2026-02-08)"
PN_SE_POSTPAKET_TERMS_URL = "https://api2.postnord.com/rest/customer/v2/ptm/file/download/5341.28764?disposition=inline (valid 2025-05-02)"
PN_SE_SERVICE_POINT_TERMS_URL = "https://www.avropa.se/globalassets/bilagor/1.-aktuella-rao/postformedlingstjanster-2021/paketformedlingstjanster--1-lev-postnord/sarskilda-villkor-service-point-2026.pdf (valid 2026-01-01)"
PN_FI_PAGE_URL = "https://www.postnord.fi/en/sending/online-tools/customs-information/ (read 2026-09-25)"
PN_FI_TERMS = "PostNord FI special terms for parcels, valid 2026-05-01 (Wayback 2026-06-10)"
PN_DK_PAGE_URL = "https://www.postnord.dk/erhverv/eksport/ (Wayback 2026-03-10)"
DHL_MAN_URL = "https://dhlpaket.se/dashboard/specifications/products/ (product manual v5.26, updated 2026-10-01, valid from 2026-11-01, sha256 050660c37ba93d1ae9514c50dfa42c2010bc87763ccaff51a740b2526af11b73)"
DHL_CIE_URL = "https://www.dhl.com/content/dam/dhl/local/se/dhl-freight/documents/pdf/se-freight-customs-information-export-en.pdf (2025-02-03)"
DHL_PRL_URL = "https://www.dhl.com/content/dam/dhl/local/se/dhl-freight/documents/pdf/se-freight-price-list-additional-services-sv.pdf (valid 2026-05-01)"
BRING_URL = "https://www.bring.se/tjanster/tull/tulldokument"
BAZG_R_69_03_URL = "https://www.bazg.admin.ch/dam/de/sd-web/mIvoM5CF7ydH/steuerbemessungsgrundlage-de.pdf (valid 2025-01-01)"
PN_SE_NO_PAGE_URL = "https://www.postnord.se/privat/skicka/skicka-brev-och-paket-utomlands/skicka-paket-till-norge/ (read 2026-10-02)"
TV_EXPORT_DOCUMENTS_URL = "https://www.tullverket.se/sv/foretag/exporteravaror/deklareravarorvidexport/styrkandehandlingarvidexport.4.78aa922815794d801e25e3.html (updated 2026-06-12, read 2026-10-02)"
DHL_EXPRESS_CUSTOMS_URL = "https://mydhl.express.dhl/content/dam/downloads/global/en/customs-guide/express_global_customs_customer_guidelines.pdf.coredownload.pdf"
DHL_CONNECTOR_REJECTION_112_GB_URL = "https://github.com/PrimePack-AB/karrio-dhl-freight-sweden/blob/28c1ccb/tests/dhl_freight_sweden/fixtures/sandbox/rejection-22005-112-se-gb.json (captured 2026-10-06)"


@attr.s(auto_attribs=True, frozen=True)
class Source:
    """One cited document or code location with its evidence tag."""

    tag: str
    reference: str
    statement: str

    def to_dict(self) -> dict:
        return attr.asdict(self)


def _ref(lines: str, location: str) -> str:
    return f"{lines}; {location}"


# PostNord Sweden

PN_SE_SERVICE_POINT_TERMS_PAPER = Source(
    "W",
    _ref("FN:118-119", PN_SE_SERVICE_POINT_TERMS_URL),
    "Service Point special terms §4: a commercial invoice \"in at least two copies in English shall accompany the parcel\", in a plastic pocket on parcel no. 1; digital data prevails over paper on discrepancy.",
)
PN_SE_SERVICE_POINT_TERMS_NORWAY = Source(
    "W",
    _ref("FN:118", PN_SE_SERVICE_POINT_TERMS_URL),
    "Service Point special terms §4: \"To Norway the commercial invoice and shipment list shall be sent digitally\".",
)
PN_SE_EN_PAGE_PARCEL_TRIPLICATE = Source(
    "W",
    _ref("FN:100, FN:142", PN_SE_EN_PAGE),
    "English customs documents page: Service Point, MyPack Home, Pallet, and Parcel need an invoice, not CN22/CN23; shipping document and invoice \"in triplicate\" (3 copies).",
)
PN_SE_SV_PAGE_PARCEL_TWO_COPIES = Source(
    "W",
    _ref("FN:142, FN:264", PN_SE_SV_PAGE),
    "Swedish customs documents page: the invoice in \"två exemplar\" (2 copies).",
)
PN_SE_PLASTIC_POCKET_ORIGIN = Source(
    "I",
    _ref("FN:148", FACTS_NOTE),
    "Neither 2026 PostNord SE web snapshot contains the plastic-pocket wording for invoices; that wording comes from the Service Point special terms.",
)
PN_SE_NORWAY_CHANNELS = Source(
    "W",
    _ref("FN:142, FN:147", PN_SE_SV_PAGE),
    "Swedish customs documents page: to Norway the invoice goes digitally, not with the parcel, through the Booking API, PostNord Skicka Direkt Business, foravisering.export@postnord.com, or upload in MyCustoms, where shippers can \"förse oss med tullinformation, eller ladda upp en tullfaktura\".",
)
PN_SE_NORWAY_ONLY_CHANNELS = Source(
    "W",
    _ref("FN:149", PN_SE_SV_PAGE),
    "None of the PostNord SE separate invoice channels is stated to apply to destinations other than Norway.",
)
PN_SE_SV_PAGE_NORWAY_LETTERS = Source(
    "W",
    _ref("FN:99, FN:108", PN_SE_SV_PAGE),
    "Swedish customs documents page, letters: \"OBS! Vid export till Norge behöver Handelsfaktura och VOEC* anges från 0 kr.\"",
)
PNS_PARCEL_CUSTOMS_INVOICE = Source(
    "S",
    _ref(
        "PNS:28-31",
        f"{PNS}; implemented on feat-postnord-customs-invoice at face88f37, merged into develop by 52d21fbfb",
    ),
    "A parcel product booked with customs data containing commodities carries a customs invoice and no CN22 or CN23 declaration.",
)
PNS_INTERNATIONAL_PARCEL_CN22 = Source(
    "S",
    _ref("PNS:10, PNS:13-16", PNS),
    "Letter services and International Parcel (postnord_postpaket_utrikes, code 91) keep sending CN22 declaration lines; no customs invoice is sent for them.",
)
PN_SE_POSTPAKET_TERMS = Source(
    "W",
    _ref("FN:103, FN:111", PN_SE_POSTPAKET_TERMS_URL),
    "Postpaket Utrikes terms §2: CN23 in two copies and a commercial invoice in 2 copies with the parcel when the goods value exceeds SEK 2 000 or the goods are sent for commercial purposes (\"För paket med varuvärde över 2000 kr eller då varan skickas i handelssyfte krävs utöver frakthandling och Exportdeklaration Post CN23, i två exemplar en handelsfaktura i 2 exemplar med paketet.\").",
)
PN_SE_EN_PAGE_POSTPAKET = Source(
    "W",
    _ref("FN:102, FN:107", PN_SE_EN_PAGE),
    "English customs documents page, EMS and Parcel Post International: \"> SEK 2,000: CN23 and commercial or pro forma invoice in triplicate.\" (3 copies, on value only).",
)
PN_SE_SV_PAGE_POSTPAKET = Source(
    "W",
    _ref("FN:102, FN:109", PN_SE_SV_PAGE),
    "Swedish customs documents page, EMS and Postpaket: \"> 2 000 kr: CN23 och handels- eller proformafaktura i tre exemplar.\" (3 copies, on value only).",
)
PN_POSTPAKET_CODE_91 = Source(
    "S",
    _ref("FN:165", "karrio modules/connectors/postnord/karrio/providers/postnord/units.py:146; modules/connectors/postnord/vendor/docs/general-descriptions.pdf"),
    "Code 91 is the contract and EDI product: postnord_postpaket_utrikes = \"91\" matches \"91 Z91 Postpaket Utrikes\" and \"International Parcel(91)\".",
)
PN_POSTPAKET_CODE_95 = Source(
    "W",
    _ref("FN:166", "https://api2.postnord.com/rest/customer/v2/ptm/file/download/5341.28763 (PostNord terms valid 2025-05-02)"),
    "Code 95 is the direct-payment product Parcel Post International (Postpaket Utrikes); its terms require two CN23 copies and three copies of the commercial invoice with the parcel above SEK 2 000 or for commercial purposes.",
)
PN_POSTPAKET_TERMS_PROFORMA = Source(
    "W",
    _ref("FN:111, FN:113", PN_SE_POSTPAKET_TERMS_URL),
    "Postpaket Utrikes terms §2: \"Proformafaktura … får endast användas vid gåva eller varuprov.\"",
)

# PostNord Finland

PN_FI_WEB_PAGE = Source(
    "W",
    _ref("FN:143, FN:152", PN_FI_PAGE_URL),
    "postnord.fi customs information: \"If necessary, the invoice can be attached to the shipment or submitted separately to support customs clearance. A copy of the invoice can be sent by email to address tullaus.fi@postnord.com [...]. Original invoices must be prepared in English and signed by hand if necessary\".",
)
PN_FI_WEB_PAGE_NORWAY = Source(
    "W",
    _ref("FN:153", PN_FI_PAGE_URL),
    "postnord.fi customs information: for Norway the electronic customs data must arrive before the shipment.",
)
PN_FI_SPECIAL_TERMS = Source(
    "W",
    _ref("FN:143, FN:154", PN_FI_TERMS),
    "PostNord FI special terms for parcels: non-EU parcels require \"a signed commercial invoice in English in triplicate\", and invoices to Norway are electronic; EDI prevails over the shipping document on discrepancy.",
)
PN_FI_GOVERNING_UNRESOLVED = Source(
    "I",
    _ref("FN:155, FN:267", FACTS_NOTE),
    "The web page appears relaxed after December 2025 while the contract terms were not; which of the two governs is unresolved.",
)

# PostNord Denmark

PN_DK_EXPORT_PAGE = Source(
    "W",
    _ref("FN:144, FN:157", PN_DK_PAGE_URL),
    "postnord.dk export: documents in a plastic pocket visible on the parcel; Norway 2 invoices, Switzerland and Liechtenstein 3, Great Britain 2, rest of world 1 CN23 and 2 invoices, the invoice \"not required\" but recommended; a lodged export declaration is copied to eksport@postnord.com.",
)

# DHL Freight Sweden

DFS_CUSTOMS_SERVICES_OPT_IN = Source(
    "S",
    _ref("DFS:75-83", DFS),
    "The connector selects a customs service (standard handling, full-service handling, customer's own declaration, joint declaration) only when the caller sets its option, because each service carries a DHL fee.",
)
DHL_MAN_CUSTOMS_SELECTION = Source(
    "W",
    _ref("FN:196", f"{DHL_MAN_URL} §7.6.1 p.163, §6.7 p.96"),
    "Customs handling (Standard or Full service) or own declaration must be selected for CH, GB, NO, Åland (FI 22) and other non-EU destinations.",
)
DHL_PRL_NO_FEE_FREE_MODE = Source(
    "W",
    _ref("FN:208", DHL_PRL_URL),
    "No fee-free customs mode exists for non-EU destinations.",
)
DHL_OWN_DECLARATION_FEE_INFERENCE = Source(
    "I",
    _ref("FN:208, FN:269", FACTS_NOTE),
    "The price list has no own-declaration line for 109 and 112, so whether DHL bills own declaration on them is inferred, not stated.",
)
DHL_MAN_INVOICE_COPY = Source(
    "W",
    _ref("FN:213", f"{DHL_MAN_URL} §7.6.2 p.163"),
    "\"A copy of the invoice must still be sent\" even with complete EDI data under standard customs handling.",
)
DHL_CIE_INVOICE_ROUTES = Source(
    "W",
    _ref("FN:214", f"{DHL_CIE_URL} p.9"),
    "The invoice copy is emailed to dhlfreight.int.se@dhl.com shortly after booking, or uploaded in myDHL Freight, one document per shipment with a clear reference.",
)
DHL_CIE_REMINDER_FEES = Source(
    "W",
    _ref("FN:216", f"{DHL_CIE_URL} p.12; {DHL_PRL_URL}"),
    "Missing documents stop the shipment, with reminder fees of 390 kr (650 kr for Great Britain).",
)
DHL_API_NO_UPLOAD = Source(
    "S",
    _ref("FN:179", "karrio modules/connectors/dhl_freight_sweden/vendor/se-api-farm/"),
    "The DHL Freight Sweden API has no attachment or upload endpoint.",
)
DHL_MAN_OUTSIDE_COPIES = Source(
    "W",
    _ref("FN:215", f"{DHL_MAN_URL} §5.14 p.62"),
    "For Parcel Connect (109): \"Two copies of customs documents must also be attached on the outside of the package\".",
)
DHL_OUTSIDE_COPIES_UNCONFIRMED = Source(
    "I",
    _ref("FN:215, FN:268", FACTS_NOTE),
    "Whether Parcel Connect Plus (112) and road-freight products require copies attached to the outside of the package is unconfirmed.",
)
DFS_VOEC_SERVICE = Source(
    "S",
    _ref("DFS:66-73", DFS),
    "A customs.options.voec_number is sent as DHL's VOEC supply VAT service with that number as its VAT identifier.",
)
DHL_MAN_VOEC_MARKING = Source(
    "W",
    _ref("FN:217", f"{DHL_MAN_URL} §6.5 p.92, §6.6 p.94, §9.4.2 p.168"),
    "The Norway VOEC ID must be printed on the package or label.",
)
DHL_MAN_VOEC_PARCEL_CONNECT = Source(
    "W",
    _ref("FN:206", f"{DHL_MAN_URL} §6.5 p.92, §6.6 p.94"),
    "The voecSupplyVAT service is VOEC with Parcel Connect (109) to Norway, sent in the API as additionalServices.voecSupplyVAT.vatId.",
)

# Invoice type

PNS_COMMERCIAL_FLAG = Source(
    "S",
    _ref("PNS:155-168", PNS),
    "customs.commercial_invoice selects the customs invoice type literally: true declares COMMERCIAL, false or omitted declares PROFORMA regardless of content_type; mismatch detection is left to advisory tooling.",
)
DFS_COMMERCIAL_FLAG = Source(
    "S",
    _ref("DFS:51-64", DFS),
    "customs.commercial_invoice selects the customs document type literally: true declares CommercialInvoice, false or omitted declares ProformaInvoice regardless of content_type.",
)
PROFORMA_FOR_GOODS_NOT_SOLD = Source(
    "W",
    _ref("FN:56", f"{BRING_URL}; {DHL_CIE_URL} p.5"),
    "The commercial invoice has no fixed format; a proforma invoice is used for goods not sold and states \"No charge. Value for customs purposes only\".",
)
CONNECTOR_FLAG_MAPPING = Source(
    "S",
    _ref("FN:30-36", "karrio modules/connectors/dhl_freight_sweden/karrio/providers/dhl_freight_sweden/shipment/create.py"),
    "Connectors that read customs.commercial_invoice map it to a commercial versus proforma invoice type, never to producing a document.",
)

# Customs values

BAZG_RABATTE = Source(
    "W",
    _ref("§5.5.3", BAZG_R_69_03_URL),
    "BAZG Richtlinie R-69-03 §5.5.3 \"Rabatte\": discounts are not part of the taxable consideration, and an item the supplier hands over with a sold item as a discount in kind or add-on (Zugabe) is not taxed additionally on import, provided it is directly connected to the supply causing the import.",
)
PN_SE_NO_PAGE_NON_ZERO_VALUE = Source(
    "W",
    _ref("Skicka paket till Norge", PN_SE_NO_PAGE_URL),
    "PostNord SE page on parcels to Norway: \"värdet på en handels- eller proformafaktura får aldrig vara 0 kronor. Allt har ett värde även om innehållet är en gåva eller ett varuprov.\"",
)
TV_PROFORMA_NON_ZERO_VALUE = Source(
    "W",
    _ref("Styrkande handlingar vid export", TV_EXPORT_DOCUMENTS_URL),
    "Tullverket, supporting documents for export: a pro forma invoice states \"värde för tulländamål för varje varuslag (får inte vara 0 kronor)\" and \"No charge. Value for customs purposes only.\", and an invoice states \"eventuella rabatter och vilken typ av rabatter\".",
)
DHL_EXPRESS_NO_ZERO_VALUES = Source(
    "W",
    _ref("Customs customer guidelines", DHL_EXPRESS_CUSTOMS_URL),
    "DHL Express customs guidelines: \"zero (0) values are not acceptable\" for line values, and invoice values must comply with WTO valuation rules.",
)
DHL_MAN_PARCEL_CONNECT_COUNTRIES = Source(
    "W",
    _ref("Product manual v5.26", f"{DHL_MAN_URL} §5.3 p.18, §5.14 p.63, §5.15 p.66"),
    "DHL Freight Sweden product manual v5.26: Parcel Connect (109) serves AT, BE, BG, CZ, DE, DK, EE, ES, FI, FR, GB (by separate agreement only), HR, HU, IE, IT, LT, LU, LV, NL, NO, PL, PT, RO, SI, and SK; Parcel Connect Plus (112) the same, FR only through the print and transportInstruction APIs; Parcel Return Connect (107) the same except GB; 109 and 112 exclude FR 97100-99999; Switzerland is served by Road Freight Standard (202), Road Freight Direct (205), Road Freight Priority (233), SPI, and Home Delivery International (601).",
)
DHL_CONNECTOR_SANDBOX_112_GB_REJECTED = Source(
    "S",
    _ref("Sandbox rejection 22005", DHL_CONNECTOR_REJECTION_112_GB_URL),
    "DHL Freight Sweden connector sandbox evidence: a Parcel Connect Plus (112) booking from SE to GB without the separate agreement, for which product matches did not offer 112, was rejected with 22005 \"No valid product was found for given productcode and countries\" and 22026 \"Consignee CountryCode is not valid for this product\".",
)

ALL: typing.Tuple[Source, ...] = tuple(
    value for value in dict(globals()).values() if isinstance(value, Source)
)
