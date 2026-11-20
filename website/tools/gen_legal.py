#!/usr/bin/env python3
"""Generate Terms of service (11655:13467) and Privacy Policy (11655:13534) pages.
Markup: blank line = paragraph, "- " = bullet, **x** = bold, "##" = section heading.
Bracketed values like [support@seemyhealth.com] are placeholders in the Figma copy; kept as-is.
"""
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "src" / "pages"

TERMS_INTRO = """Welcome, and thank you for choosing SeeMyHealth. Please read these Terms of Service carefully before using our products or services. By purchasing our products or using our app, you agree to be bound by these terms.

These Terms of Service ("Terms") are a legally binding agreement between you and SeeMyHealth. They govern your use of our website at [www.seemyhealth.com], our mobile application (the "App"), and all hardware products we offer — including The Ring One, Smart Scale, Blood Pressure Monitor, and Smart Flask (collectively, the "Products") — as well as any related services (together, the "Services").

If you do not agree to these Terms, please do not use our Services."""

TERMS = [
 ("Overview of Services", """SeeMyHealth offers a suite of health-monitoring hardware and a companion mobile application designed to help you track and understand your personal health data. Our Products — The Ring One, Smart Scale, Blood Pressure Monitor, and Smart Flask — connect to the SeeMyHealth App to give you a unified view of your wellness.

Important: SeeMyHealth Products and the App are designed for general wellness and informational purposes only. They are not medical devices and are not intended to diagnose, treat, cure, or prevent any medical condition. Always consult a qualified healthcare professional for medical advice."""),
 ("Eligibility & Account", """You must be at least **18 years of age** (or the minimum legal age in your country of residence, if higher) and have the legal capacity to enter into a binding contract in order to use our Services.

When creating an account, you agree to provide accurate and current information and to keep your login credentials confidential. You are responsible for all activity that occurs under your account. If you suspect any unauthorized access, notify us immediately at **[support@seemyhealth.com]**. We reserve the right to suspend or terminate accounts that are found to be inaccurate, misused, or in violation of these Terms."""),
 ("Payment & Subscriptions", """All product prices are listed on our website and may be subject to applicable local taxes, duties, or import fees, which are your responsibility. We reserve the right to update pricing at any time; changes will not affect confirmed orders.

By placing an order, you authorize SeeMyHealth — or our designated payment processor — to charge your provided payment method for the full amount of your purchase, including any applicable taxes.
The SeeMyHealth App may offer optional premium subscription plans in the future. If and when available, subscriptions will auto-renew each billing period unless canceled by you beforehand. We will clearly communicate all fees and billing terms prior to any subscription purchase, and you may cancel at any time through your account settings or by contacting **[support@seemyhealth.com]**. These Terms will be updated with full subscription details at launch."""),
 ("Delivery & Returns", """Orders will be shipped to the address provided at checkout. Delivery estimates are provided for reference only and are not guaranteed. Risk of loss and title transfer to you once your order is handed to the shipping carrier. For international orders, any customs duties or import taxes are your responsibility.

If you are not satisfied with your purchase, you may return most Products within **30 days** of delivery, provided they are in original condition and packaging and accompanied by proof of purchase. To initiate a return, contact us at **[support@seemyhealth.com]**. Refunds will be processed to your original payment method within **[10–14 business days]** of receiving the returned item. Returns that do not meet these conditions may be refused or subject to a partial refund."""),
 ("App License & Usage", """Subject to your compliance with these Terms, SeeMyHealth grants you a limited, non-exclusive, non-transferable, revocable license to use the SeeMyHealth App on a personal device you own or control, solely for personal, non-commercial use.

You may not copy, modify, reverse-engineer, or create derivative works of the App; rent, sell, or sublicense it to any third party; or use automated tools to access or interact with the App or our website. We may release updates to the App from time to time and may suspend or restrict access for operational reasons without prior notice. We recommend keeping the App updated to ensure the best experience."""),
 ("Health Data & Privacy", """Our Products and App collect health-related data — such as heart rate, blood pressure, body composition, and hydration levels — to provide you with personal wellness insights. You acknowledge that this data is provided for informational purposes only, is not clinically validated, and should not be used as the basis for medical decisions.

All personal data we collect is handled in accordance with our **Privacy Policy**, which is incorporated into these Terms by reference. By using our Services, you consent to the data practices described therein."""),
 ("Intellectual Property", """All content and materials associated with the Services — including the App, website design, product designs, logos, graphics, and software — are owned by or licensed to SeeMyHealth and protected by applicable intellectual property laws worldwide. You are not granted any ownership rights in any of our content.

"SeeMyHealth" and all related marks are our trademarks and may not be used without our prior written permission. If you share Feedback (ideas, suggestions, or recommendations) with us, you grant SeeMyHealth a perpetual, royalty-free license to use that Feedback for any purpose, without obligation to compensate or credit you."""),
 ("Prohibited Conduct", """When using our Services, you agree not to:

- Use the Services for any unlawful purpose or in violation of these Terms;
- Impersonate any person or entity, or misrepresent your affiliation;
- Attempt to gain unauthorized access to our systems, other user accounts, or any part of the Services;
- Interfere with or disrupt the performance or integrity of the Services;
- Use automated tools (bots, scrapers, etc.) to access or harvest data from the Services;
- Resell or commercially exploit the Services without our prior written consent; or
- Assist or encourage any third party to engage in any of the above.

Violations may result in the immediate suspension or termination of your access to the Services."""),
 ("Disclaimers & Warranties", """Our Services are provided on an "as is" and "as available" basis. To the fullest extent permitted by applicable law, SeeMyHealth disclaims all warranties, express or implied, including implied warranties of merchantability, fitness for a particular purpose, and non-infringement.

**Limited Product Warranty:** SeeMyHealth warrants to the original purchaser that hardware Products are free from defects in materials and workmanship for **twelve (12) months** from the date of purchase. Within this period, we will repair or replace any defective Product at no charge. This warranty does not cover normal wear and tear, accidental damage, misuse, unauthorized modifications, or products purchased from unauthorized resellers. If local consumer protection laws in your country require a longer warranty period, this warranty will be extended accordingly."""),
 ("Limitation of Liability & Indemnification", """To the fullest extent permitted by applicable law, SeeMyHealth and its affiliates, officers, and employees will not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of the Services. Our total liability to you for any claim will not exceed the amount you paid to SeeMyHealth in the **twelve (12) months** prior to the event giving rise to the claim.

You agree to indemnify and hold SeeMyHealth harmless from any claims, losses, or expenses — including reasonable legal fees — arising from your use of the Services, your violation of these Terms, or your violation of any applicable law."""),
 ("Dispute Resolution & Termination", """**Disputes:** If you have a concern, please contact us first at **[legal@seemyhealth.com]** — most issues can be resolved informally. These Terms are governed by the laws of **[Governing Jurisdiction].** For disputes that cannot be resolved informally, both parties agree to submit to the exclusive jurisdiction of the courts in **[City, Country].** Nothing in these Terms limits any rights you may have as a consumer under the mandatory laws of your country of residence.

**Termination:** You may stop using our Services at any time. To delete your account, contact **[support@seemyhealth.com].** We reserve the right to suspend or terminate your access at any time if we reasonably believe you have violated these Terms or engaged in harmful or fraudulent conduct. Upon termination, your App license immediately ceases. Provisions that by their nature should survive termination — including intellectual property, disclaimers, liability, and dispute resolution — will remain in effect."""),
 ("General", """**Changes to These Terms:** We may update these Terms from time to time. We will notify you of material changes by updating the "Last Updated" date and, where appropriate, via email or in-App notification. Continued use of the Services after the effective date of any changes constitutes your acceptance.

**Third-Party Services:** Our Services may link to or integrate with third-party platforms (e.g., payment processors, health platforms). These services are not under our control, and we are not responsible for their content or practices. Review their terms independently before sharing your data.

**Miscellaneous:** These Terms, together with our Privacy Policy, constitute the entire agreement between you and SeeMyHealth. If any provision is found unenforceable, the remaining provisions remain in full effect. Our failure to enforce any right is not a waiver of that right. You may not assign your rights under these Terms without our written consent."""),
]

PRIVACY_INTRO = """Your health data is personal — and we treat it that way. This Privacy Policy explains what data we collect, how we use it, and the choices you have when you use our Services.

This Policy applies to **[SeeMyHealth Legal Entity Name]** ("SeeMyHealth," "we," "us," or "our") and covers data collected through our website, mobile application (the "App"), and all hardware products — including The Ring One, Smart Scale, Blood Pressure Monitor, and Smart Flask — and any related services (together, the "Services").
By using our Services, you agree to the practices described here. Questions? Reach us at **[privacy@seemyhealth.com].**"""

PRIVACY = [
 ("Data We Collect", """**Data you provide directly:**

- Account details — name, email address, password, date of birth;
- Health profile — height, weight, biological sex, and any other information you choose to enter;
- Purchase information — billing and shipping address (payment card data is handled securely by our third-party payment processors; we do not store full card numbers);
- Communications — messages, feedback, or support requests you send us.

**Data collected automatically:**

- Health and biometric data — depending on the Products you use, this may include heart rate, blood pressure readings, body weight and composition, hydration levels, and sleep patterns;
- Device and usage data — device type, operating system, app version, IP address, and how you interact with the App;
- Website analytics — browsing behavior, pages visited, and session data collected via cookies and similar technologies. See our **Cookie Policy** for details."""),
 ("How We Use Your Data", """We use the data we collect to:

- Operate and improve our Products and Services, and generate health insights for you;
- Process your orders and manage your account;
- Communicate with you — including order updates, account notices, and (with your consent) marketing;
- Analyze usage patterns to develop new features and fix issues;
- Detect and prevent fraud or unauthorized access;
- Comply with legal obligations in the jurisdictions where we operate.

**Important:** The data generated by our Products is for personal wellness purposes only and is not clinically validated. It is not a substitute for professional medical advice.

We may also use aggregated, anonymized data — which cannot identify you — for analytics, research, and business development."""),
 ("Sharing & Disclosure", """We do not sell your personal data. We share it only in the following circumstances:

- **Service providers** — Trusted vendors (hosting, payments, analytics, customer support) who process data on our behalf and are bound by confidentiality obligations;
- **Third-party integrations** — If you choose to connect your data to platforms like Apple Health or Google Health Connect, you are directing us to share your data with those services, which are governed by their own privacy policies;
- **Legal obligations** — When required by law, court order, or valid government request. Where legally permitted, we will notify you first;
- **Business transfers** — In the event of a merger or acquisition, your data may be transferred as part of that transaction. We will notify you in advance."""),
 ("Data Retention", """We keep your data for as long as your account is active or as reasonably necessary to provide our Services, meet legal obligations, and resolve disputes. If you delete your account, your personal data will be deleted or anonymized within [30–90 days], except where retention is required by law. You can request deletion at any time — see Section 5 below."""),
 ("Your Rights & Choices", """Depending on where you live, you may have the right to access, correct, delete, or export your personal data, withdraw consent, or object to certain types of processing. We aim to honor these rights regardless of your location.

To make a request, contact us at **[privacy@seemyhealth.com]** or through the App settings. We will respond within **30 days.**

- **Marketing emails** — Unsubscribe at any time via the link in any email or through your App preferences.
- **Push notifications** — Manage through your device settings.
- **Regional rights** — If you are in the EEA or UK, you have rights under GDPR and may lodge a complaint with your local supervisory authority. If you are in California, you have rights under the CCPA/CPRA including the right to know, delete, and opt out of any sale of personal information (note: we do not sell personal information)."""),
 ("Data Security", """We use industry-standard measures — including encryption in transit and at rest, access controls, and regular security reviews — to protect your data. No system is completely secure, but we are committed to notifying you promptly if a breach occurs that is likely to affect your rights or interests.

To help protect your account, use a strong and unique password and enable any additional security features available in the App."""),
 ("Updates to This Policy", """We may update this Policy from time to time. When we do, we will revise the "Last Updated" date and notify you of material changes via email or in-App notification. Continued use of our Services after any changes takes effect constitutes your acceptance.

Our Services are not directed at children under the age of 16. If you believe we have collected data from a child in error, please contact us and we will delete it promptly."""),
]

CONTACT = """[SeeMyHealth Legal Entity Name]

Email address: [legal@seemyhealth.com]
Website: [www.seemyhealth.com]
Address: [Company Address]

© 2026 SeeMyHealth. All rights reserved."""


def md(text):
    text = text.replace("&", "&amp;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    out = []
    for block in text.split("\n\n"):
        lines = block.split("\n")
        if all(l.startswith("- ") for l in lines):
            out.append("<ul>" + "".join(f"<li>{l[2:]}</li>" for l in lines) + "</ul>")
        else:
            out.append("<p>" + "<br>".join(lines) + "</p>")
    return "".join(out)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def page(route, figma, title, h1, lede, intro, sections, desc):
    toc = "".join(f'<li><a href="#{route}-{slug(h)}">{h.replace("&", "&amp;")}</a></li>' for h, _ in sections)
    body = [f'<div class="legal__intro t-body">{md(intro)}</div>']
    for i, (h, t) in enumerate(sections, 1):
        body.append(f'<section class="legal__sec" id="{route}-{slug(h)}"><h2 class="t-xl">{i}. {h.replace("&", "&amp;")}</h2><div class="t-body">{md(t)}</div></section>')
    body.append(f'<section class="legal__sec" id="{route}-contact"><h2 class="t-xl">Contact Us</h2><div class="t-body">{md(CONTACT)}</div></section>')
    return f'''<!-- meta title="{title} | SeeMyHealth" description="{desc}" nav="dark" -->
<!-- figma: {figma}. Generated by tools/gen_legal.py -->
<section class="section theme-dark subpage-hero subpage-hero--legal" aria-labelledby="{route}-title">
  <div class="container subpage-hero__inner">
    <div class="subpage-hero__copy">
      <p class="eyebrow">Last updated: 1 May 2026</p>
      <h1 id="{route}-title" class="t-h2">{h1}</h1>
      <p class="t-body">{lede}</p>
    </div>
  </div>
</section>
<section class="section subpage-body" aria-label="{title}">
  <div class="subpage-card legal">
    <nav class="legal__toc t-xs" aria-label="On this page"><ul>{toc}</ul></nav>
    <div class="legal__body">
      {"".join(body)}
    </div>
  </div>
</section>
'''


if __name__ == "__main__":
    (OUT / "terms.html").write_text(page("terms", "11655:13467 Terms of service", "Terms of Service", "Terms of service",
        "Learn about the terms and conditions of our products and services.", TERMS_INTRO, TERMS,
        "The terms and conditions that govern SeeMyHealth products, the app and related services."), encoding="utf-8")
    (OUT / "privacy.html").write_text(page("privacy", "11655:13534 Privacy Policy", "Privacy Policy", "Privacy policy",
        "Learn how we collect, use, and protect your personal data when you use our products and services.", PRIVACY_INTRO, PRIVACY,
        "How SeeMyHealth collects, uses and protects your personal and health data."), encoding="utf-8")
    print("wrote terms, privacy")
