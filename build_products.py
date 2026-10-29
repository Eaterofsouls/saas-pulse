import csv
import pandas as pd
from pathlib import Path

COMPANIES_CSV = Path("saas_pulse/dataset/companies.csv")
PRODUCTS_CSV = Path("saas_pulse/dataset/products.csv")

# Known domain map for the 100 public SaaS companies
domain_map = {
    "CRM": ("Salesforce", "salesforce.com"),
    "ADBE": ("Adobe", "adobe.com"),
    "NOW": ("ServiceNow", "servicenow.com"),
    "WDAY": ("Workday", "workday.com"),
    "INTU": ("Intuit", "intuit.com"),
    "ADSK": ("Autodesk", "autodesk.com"),
    "TEAM": ("Atlassian", "atlassian.com"),
    "HUBS": ("HubSpot", "hubspot.com"),
    "SNOW": ("Snowflake", "snowflake.com"),
    "DDOG": ("Datadog", "datadoghq.com"),
    "CRWD": ("CrowdStrike", "crowdstrike.com"),
    "ZS": ("Zscaler", "zscaler.com"),
    "OKTA": ("Okta", "okta.com"),
    "TWLO": ("Twilio", "twilio.com"),
    "ZM": ("Zoom", "zoom.us"),
    "DOCU": ("DocuSign", "docusign.com"),
    "BOX": ("Box", "box.com"),
    "DBX": ("Dropbox", "dropbox.com"),
    "ASAN": ("Asana", "asana.com"),
    "ESTC": ("Elastic", "elastic.co"),
    "MDB": ("MongoDB", "mongodb.com"),
    "NET": ("Cloudflare", "cloudflare.com"),
    "PATH": ("UiPath", "uipath.com"),
    "PLTR": ("Palantir", "palantir.com"),
    "VEEV": ("Veeva", "veeva.com"),
    "PCTY": ("Paylocity", "paylocity.com"),
    "PAYC": ("Paycom", "paycom.com"),
    "BILL": ("BILL", "bill.com"),
    "FIVN": ("Five9", "five9.com"),
    "RNG": ("RingCentral", "ringcentral.com"),
    "EGHT": ("8x8", "8x8.com"),
    "BRZE": ("Braze", "braze.com"),
    "AMPL": ("Amplitude", "amplitude.com"),
    "SPT": ("Sprout Social", "sproutsocial.com"),
    "SEMR": ("Semrush", "semrush.com"),
    "WK": ("Workiva", "workiva.com"),
    "APPF": ("AppFolio", "appfolio.com"),
    "GWRE": ("Guidewire", "guidewire.com"),
    "MANH": ("Manhattan Associates", "manh.com"),
    "PEGA": ("Pegasystems", "pega.com"),
    "TYL": ("Tyler Technologies", "tylertech.com"),
    "FRSH": ("Freshworks", "freshworks.com"),
    "PD": ("PagerDuty", "pagerduty.com"),
    "DT": ("Dynatrace", "dynatrace.com"),
    "S": ("SentinelOne", "sentinelone.com"),
    "QLYS": ("Qualys", "qualys.com"),
    "TENB": ("Tenable", "tenable.com"),
    "RPD": ("Rapid7", "rapid7.com"),
    "VRNS": ("Varonis", "varonis.com"),
    "GTLB": ("GitLab", "gitlab.com"),
    "CFLT": ("Confluent", "confluent.io"),
    "DOCN": ("DigitalOcean", "digitalocean.com"),
    "FSLY": ("Fastly", "fastly.com"),
    "NCNO": ("nCino", "ncino.com"),
    "ALKT": ("Alkami", "alkami.com"),
    "QTWO": ("Q2", "q2.com"),
    "PRO": ("PROS", "pros.com"),
    "BLKB": ("Blackbaud", "blackbaud.com"),
    "ZI": ("ZoomInfo", "zoominfo.com"),
    "BL": ("BlackLine", "blackline.com"),
    "PRGS": ("Progress", "progress.com"),
    "CVLT": ("Commvault", "commvault.com"),
    "NTNX": ("Nutanix", "nutanix.com"),
    "SPSC": ("SPS Commerce", "spscommerce.com"),
    "KVYO": ("Klaviyo", "klaviyo.com"),
    "IOT": ("Samsara", "samsara.com"),
    "PCOR": ("Procore", "procore.com"),
    "OTEX": ("OpenText", "opentext.com"),
    "FROG": ("JFrog", "jfrog.com"),
    "TOST": ("Toast", "toasttab.com"),
    "RAMP": ("LiveRamp", "liveramp.com"),
    "YEXT": ("Yext", "yext.com"),
    "PANW": ("Palo Alto Networks", "paloaltonetworks.com"),
    "FTNT": ("Fortinet", "fortinet.com"),
    "AKAM": ("Akamai", "akamai.com"),
    "PTC": ("PTC", "ptc.com"),
    "CDNS": ("Cadence", "cadence.com"),
    "SNPS": ("Synopsys", "synopsys.com"),
    "CXM": ("Sprinklr", "sprinklr.com"),
    "DUOL": ("Duolingo", "duolingo.com"),
    "APP": ("AppLovin", "applovin.com"),
    "GEN": ("Gen Digital", "gendigital.com"),
    "BLND": ("Blend Labs", "blend.com"),
    "TASK": ("TaskUs", "taskus.com"),
    "LAW": ("CS Disco", "csdisco.com"),
    "COUR": ("Coursera", "coursera.org"),
    "FLYW": ("Flywire", "flywire.com"),
    "PAY": ("Paymentus", "paymentus.com"),
    "YOU": ("CLEAR", "clearme.com"),
    "CALX": ("Calix", "calix.com"),
    "CSGP": ("CoStar Group", "costargroup.com"),
    "BAND": ("Bandwidth", "bandwidth.com"),
    "MKTX": ("MarketAxess", "marketaxess.com"),
    "TWST": ("Twist Bioscience", "twistbioscience.com"),
    "VERX": ("Vertex", "vertexinc.com"),
    "AGYS": ("Agilysys", "agilysys.com"),
    "ALRM": ("Alarm.com", "alarm.com"),
    "APPN": ("Appian", "appian.com"),
    "BLZE": ("Backblaze", "backblaze.com"),
    "FOUR": ("Shift4 Payments", "shift4.com")
}

# The 30 private / specified products in Step E:
private_products = [
    ("Notion", "notion.so", ""),
    ("Canva", "canva.com", ""),
    ("Zapier", "zapier.com", ""),
    ("Airtable", "airtable.com", ""),
    ("Linear", "linear.app", ""),
    ("Intercom", "intercom.com", ""),
    ("Calendly", "calendly.com", ""),
    ("Miro", "miro.com", ""),
    ("Webflow", "webflow.com", ""),
    ("Grammarly", "grammarly.com", ""),
    ("Gusto", "gusto.com", ""),
    ("Rippling", "rippling.com", ""),
    ("Retool", "retool.com", ""),
    ("ClickUp", "clickup.com", ""),
    ("Pipedrive", "pipedrive.com", ""),
    ("Zendesk", "zendesk.com", ""),
    ("Mixpanel", "mixpanel.com", ""),
    ("Typeform", "typeform.com", ""),
    ("Vercel", "vercel.com", ""),
    ("Supabase", "supabase.com", ""),
    ("Postman", "postman.com", ""),
    ("Lucid", "lucidchart.com", ""),
    ("Loom", "loom.com", ""),
    ("Trello", "trello.com", ""),
    ("Slack", "slack.com", ""),
    ("Asana", "asana.com", "ASAN"),
    ("Monday", "monday.com", "MNDY"),
    ("Figma", "figma.com", ""),
    ("Shopify", "shopify.com", "SHOP"),
    ("Stripe", "stripe.com", "")
]

def main():
    df = pd.read_csv(COMPANIES_CSV)
    products = []
    seen_domains = set()

    # Public SaaS companies
    for _, row in df.iterrows():
        ticker = row["ticker"]
        name = row["name"]
        prod_name, domain = domain_map.get(ticker, (name, f"{ticker.lower()}.com"))
        if domain not in seen_domains:
            seen_domains.add(domain)
            products.append({
                "product": prod_name,
                "domain": domain,
                "public_ticker_or_blank": ticker
            })

    # Additional private products
    for prod_name, domain, ticker in private_products:
        if domain not in seen_domains:
            seen_domains.add(domain)
            products.append({
                "product": prod_name,
                "domain": domain,
                "public_ticker_or_blank": ticker
            })

    out_df = pd.DataFrame(products)
    out_df.to_csv(PRODUCTS_CSV, index=False)
    print(f"Saved {len(out_df)} products to {PRODUCTS_CSV}")

if __name__ == "__main__":
    main()
