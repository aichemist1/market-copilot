from __future__ import annotations


SAMPLE_HOUSE_PTR_XML = """\
<root>
  <record>
    <FilingID>20034202</FilingID>
    <Name>Hon. Rob Bresnahan</Name>
    <FilingType>Periodic Transaction Report</FilingType>
    <FilingDate>2026-03-18</FilingDate>
    <FilingStatus>New</FilingStatus>
    <StateDistrict>PA08</StateDistrict>
    <PDFUrl>https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2026/20034202.pdf</PDFUrl>
  </record>
  <record>
    <FilingID>20034522</FilingID>
    <Name>Hon. Brian Babin</Name>
    <FilingType>Periodic Transaction Report</FilingType>
    <FilingDate>2026-05-18</FilingDate>
    <FilingStatus>New</FilingStatus>
    <StateDistrict>TX36</StateDistrict>
    <PDFUrl>https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2026/20034522.pdf</PDFUrl>
  </record>
</root>
"""


SAMPLE_HOUSE_PTR_XML_WITH_FAILURE = """\
<root>
  <record>
    <FilingID>20039999</FilingID>
    <Name>Failure Path Sample</Name>
    <FilingType>Periodic Transaction Report</FilingType>
    <FilingDate>2026-05-31</FilingDate>
    <FilingStatus>New</FilingStatus>
    <StateDistrict>TX07</StateDistrict>
    <PDFUrl>https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2026/20039999.pdf</PDFUrl>
  </record>
</root>
"""
