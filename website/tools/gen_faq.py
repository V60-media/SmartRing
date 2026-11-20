#!/usr/bin/env python3
"""Generate src/pages/faq.html. Figma: 11655:13591…11655:14031 (FAQ - General … Warranty & Support).
Answer markup: blank line = new paragraph, "- " = bullet, **x** = bold.
"""
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "src" / "pages" / "faq.html"

FAQ = [
 ("general", "General", [
  ("What is SeeMyHealth?", "SeeMyHealth is a health technology brand that makes smart devices designed to fit seamlessly into your everyday life. Our ecosystem — Ring One, Smart Scale, BP Monitor, and Smart Flask — works together to give you a continuous, connected picture of your health, not just a snapshot.\n\nThink of it less like monitoring yourself, and more like having a quiet companion that pays attention so you don't have to."),
  ("How does the SeeMyHealth ecosystem work?", "Each SeeMyHealth device tracks specific health metrics and syncs automatically to the SeeMyHealth app. The app brings everything together — sleep, heart rate, blood pressure, weight, hydration, and more — in one place, so you can see how your habits connect and where small changes make the biggest difference.\n\nYou don't need to check in constantly. SeeMyHealth runs quietly in the background and surfaces what matters when it matters."),
  ("Do I need all the products to get started?", "Not at all. Each SeeMyHealth device works on its own and delivers value right out of the box. That said, using more devices together gives you a fuller, more connected view of your health — patterns become clearer, and insights become more actionable.\n\nStart with what feels most relevant to your health goals, and build from there."),
  ("Is SeeMyHealth suitable for people with medical conditions?", "SeeMyHealth devices are designed for general health and wellness tracking and are not intended to diagnose, treat, or replace professional medical advice. That said, many users with chronic conditions such as hypertension, diabetes, or sleep disorders find continuous tracking helpful for staying aware and informed.\n\nIf you have an existing condition, we recommend consulting your healthcare provider before using SeeMyHealth as part of your care routine."),
  ("What makes SeeMyHealth different from other health wearables?", "Most health devices are built to be noticed — on your wrist, in your ear, on your chest. SeeMyHealth takes a different approach. Our devices are designed to disappear into your daily routine: a ring you forget you're wearing, a scale that takes 10 seconds, a flask that tracks hydration without you thinking about it.\n\nWe're not building a status symbol. We're building tools that make staying healthy feel less like work."),
 ]),
 ("products", "Products", [
  ("What is Ring One, and what does it track?", "Ring One is SeeMyHealth's smart ring — worn on your finger, it tracks your health around the clock without getting in the way of your day. It continuously monitors:\n\n- Sleep quality and stages\n- Heart rate and resting heart rate\n- Heart rate variability (HRV) — a key indicator of stress and recovery\n- Activity and movement patterns\n- Body temperature trends\n\nAll data syncs automatically to the SeeMyHealth app while you sleep, work, and move through your day."),
  ("How long does Ring One's battery last?", "Ring One is designed for up to 7 days of continuous use on a single charge. Actual battery life may vary depending on usage patterns and features enabled. A full charge takes approximately 60–80 minutes using the included charging dock.\n\nWe recommend charging overnight every few days to keep things uninterrupted."),
  ("Is Ring One waterproof?", "Yes. Ring One is water-resistant up to 100 meters, making it safe to wear while washing your hands, swimming, or showering. It's designed to stay on — all day, every day."),
  ("What does the Smart Scale measure beyond just weight?", "The Smart Scale goes well beyond the number on the floor. A single weigh-in takes about 10 seconds and gives you:\n\n- Body weight\n- Body fat percentage\n- Muscle mass\n- Bone density\n- Visceral fat level\n- BMI\n- Body water percentage\n\nAll measurements sync instantly to the SeeMyHealth app, where you can track trends over time rather than fixating on a single reading."),
  ("How does the BP Monitor work?", "The SeeMyHealth BP Monitor is a clinical-grade blood pressure monitor that delivers accurate readings in under 30 seconds. Simply wrap the cuff around your upper arm, press the button, and your systolic, diastolic, and pulse readings are automatically recorded and logged in the app.\n\nIt uses oscillometric measurement technology and meets international accuracy standards. Readings are timestamped and tracked over time so you and your healthcare provider can see trends, not just individual data points."),
  ("What is the Smart Flask, and how does it tracks hydration?", "The Smart Flask is a hydration-tracking water bottle that monitors how much you drink throughout the day. Built-in sensors detect liquid intake and sync data to the SeeMyHealth app in real time. You can set daily hydration goals, receive gentle reminders, and review your intake patterns over days and weeks.\n\nIt's available in multiple sizes and is made from BPA-free, food-grade materials. Works with both hot and cold liquids."),
  ("When will the Glucometer be available?", "The SeeMyHealth Glucometer is currently in development and will be joining the ecosystem soon. It will allow for seamless glucose tracking that integrates directly with your existing SeeMyHealth health data — giving a fuller picture for those managing metabolic health.\n\nSign up for our newsletter to be the first to know when it launches."),
 ]),
 ("app", "App &amp; Data", [
  ("What app do I use with SeeMyHealth devices?", "All SeeMyHealth devices are managed through the SeeMyHealth app, available on iOS and Android. The app is your central dashboard — it aggregates data from all your devices, surfaces trends and insights, and lets you set goals, reminders, and health targets.\n\nThe app is free to download. Some advanced features and report exports may require a subscription plan."),
  ("Which smartphones are compatible?", "The SeeMyHealth app is compatible with:\n\n- **iOS**: iPhone running iOS 14 or later\n- **Android**: Devices running Android 8.0 or later\n\nDevices sync via Bluetooth. An internet connection is required for initial setup, cloud backup, and accessing historical data on new devices. Core tracking features continue to function offline."),
  ("How is my health data stored and protected?", "Your health data is encrypted in transit and at rest. SeeMyHealth stores your data on secure, cloud-based servers and complies with applicable data protection regulations including GDPR.\n\nWe do not sell your personal health data to third parties. You have full control over your data — you can export, delete, or revoke access at any time from within the app."),
  ("Can I share my data with my doctor or healthcare provider?", "Yes. The SeeMyHealth app allows you to generate detailed health reports — including sleep, heart rate, blood pressure, hydration, and body composition trends — that can be downloaded as a PDF and shared directly with your healthcare provider.\n\nYou can also grant view-only access to a healthcare professional through the app's sharing settings, if your provider uses the SeeMyHealth for Business platform."),
  ("Does the app work without an internet connection?", "SeeMyHealth devices will continue to sync data to the app over Bluetooth without an internet connection. Your data is stored locally on your phone and will sync to the cloud the next time you're online.\n\nAn internet connection is required for initial account setup, software updates, and accessing data across multiple devices."),
 ]),
 ("orders", "Orders &amp; Shipping", [
  ("Where can I buy SeeMyHealth products?", "SeeMyHealth products are available directly at seemyhealth.com and through selected authorized retail and healthcare partners. Purchasing directly from us ensures you receive the full warranty, the latest firmware, and access to our customer support team.\n\nIf you purchased from a retailer, any returns or exchanges must be handled directly with that retailer."),
  ("How long does shipping take, and can I track my order?", "Most orders are processed and dispatched within 1–2 business days. Standard delivery typically takes 3–7 business days depending on your location. Estimated delivery times are shown at checkout.\n\nOnce your order ships, you'll receive a confirmation email with a tracking number. Click the tracking number in the email to follow your delivery directly on the carrier's website."),
  ("Do you ship internationally? Are there any import fees?", "Yes, we ship to selected countries across Asia, North America, Europe, and Australia. Available shipping destinations and fees are shown at checkout based on your delivery address.\n\nDepending on your country's customs regulations, import duties or taxes may apply upon delivery. These charges are outside of SeeMyHealth's control and are the responsibility of the recipient. We recommend checking your local customs regulations if you're unsure."),
  ("Can I change or cancel my order after placing it?", "You can cancel or modify your order as long as it hasn't been dispatched. Contact us as soon as possible at **support@seemyhealth.com** with your order number.\n\nOnce an order has shipped, modifications are no longer possible. You're welcome to return the item after delivery in accordance with our return policy."),
  ("What is your return and refund policy?", "We accept returns within 30 days of delivery for any reason, provided the product is in its original condition and packaging. Original shipping fees are non-refundable.\n\nTo initiate a return, email **support@seemyhealth.com** with your order number. Once we receive and inspect the item, refunds are processed within 3–5 business days to your original payment method."),
 ]),
 ("warranty", "Warranty &amp; Support", [
  ("What does the SeeMyHealth warranty cover?", "All SeeMyHealth devices are covered by a limited warranty that protects against defects in materials and workmanship under normal use. Coverage periods from date of purchase are as follows:\n\n- **Ring One**: 1 year\n- **Smart Scale**: 1 year\n- **BP Monitor**: 2 years\n- **Smart Flask**: 1 year\n\nThe warranty applies to products purchased directly from seemyhealth.com or through an authorized retailer. Proof of purchase is required to submit a claim.\n\nThe following are not covered: accidental damage, physical damage from drops or impact, cosmetic wear and tear, water damage beyond each device's rated resistance, and any modifications not authorized by SeeMyHealth."),
  ("What can I expect if my device is replaced under warranty?", "If your device is eligible for a warranty replacement, we'll provide a unit that's comparable to your original. Replacements may be like-new devices that have been thoroughly cleaned, factory reset, and tested to meet our quality standards.\n\nYour replacement will be covered for the remainder of your original warranty period, or 90 days from delivery — whichever is longer."),
  ("How do I submit a warranty claim?", "If you think your device may have a defect, reach out to us at **support@seemyhealth.com**. To help us review your case as quickly as possible, please include:\n\n- Your order number\n- A brief description of the issue\n- Photos or a short video showing the problem, if applicable\n- The product model and, for Ring One, the size\n\nOur team aims to respond within 1 business day and will guide you through the next steps."),
  ("Can I extend my warranty coverage?", "Yes. Extended protection plans are available for purchase at checkout when buying a new SeeMyHealth device. These plans extend your coverage beyond the standard warranty period and include protection against accidental damage such as drops or physical impact — which is not covered under the standard limited warranty.\n\nProtection plans can only be added at the time of purchase and cannot be applied retroactively."),
  ("What if my Ring One doesn't fit?", "Ring One is available in sizes 6 through 13. We recommend using our Ring Sizing Guide — available on the product page and as a printable PDF — before placing your order.\n\nIf your ring doesn't fit upon arrival, we offer a free size exchange within 30 days of delivery. Contact our support team with your order number and the size you need, and we'll sort it out."),
  ("How do I clean and maintain my devices?", "**Ring One**: Wipe with a soft, lint-free cloth. Avoid abrasive materials or chemical cleaners. Remove from the charging dock when not actively charging to help preserve battery health over time.\n\n**Smart Scale**: Wipe the surface with a dry or slightly damp cloth. Do not submerge or expose to excessive moisture. For accurate readings, always place it on a flat, hard surface.\n\n**BP Monitor**: Wipe the cuff and unit with a clean, dry cloth after use. Do not wash the cuff with water. Store in the included case when not in use to protect the cuff fabric.\n\n**Smart Flask**: The outer shell and lid are dishwasher-safe on the top rack. Hand wash the sensor-equipped base with mild soap and warm water. Do not fully submerge the base.\n\nRoutine cleaning helps maintain accurate readings and extends the lifespan of your devices."),
 ]),
]


def md(text):
    text = text.replace("&", "&amp;").replace("&amp;amp;", "&amp;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    out = []
    for block in text.split("\n\n"):
        lines = block.split("\n")
        if all(l.startswith("- ") for l in lines):
            out.append("<ul>" + "".join(f"<li>{l[2:]}</li>" for l in lines) + "</ul>")
        else:
            out.append(f"<p>{block}</p>")
    return "".join(out)


def build():
    tabs, panels = [], []
    for i, (key, label, qa) in enumerate(FAQ):
        sel = "true" if i == 0 else "false"
        tabs.append(f'<button role="tab" type="button" class="faq-tab" data-tab="{key}" aria-selected="{sel}" aria-controls="faq-panel-{key}" id="faq-tab-{key}"{"" if i == 0 else " tabindex=\"-1\""}>{label}</button>')
        items = []
        for j, (q, a) in enumerate(qa):
            items.append(f'''      <li class="faq-qa"><button class="accordion__btn faq-qa__btn" type="button" aria-expanded="{"true" if j == 0 else "false"}"><span class="t-md faq-qa__q">{q.replace("&", "&amp;")}</span><span class="faq-qa__icon" aria-hidden="true"></span></button>
        <div class="accordion__panel"><div class="faq-qa__a t-body">{md(a)}</div></div></li>''')
        panels.append(f'''    <div role="tabpanel" class="faq-panel" id="faq-panel-{key}" data-tab="{key}" aria-labelledby="faq-tab-{key}"{"" if i == 0 else " hidden"}>
      <ul class="faq-list">
{chr(10).join(items)}
      </ul>
    </div>''')
    html = f'''<!-- meta title="FAQ | SeeMyHealth" description="Answers about SeeMyHealth devices, the app and your data, orders and shipping, and warranty and support." nav="dark" -->
<!-- figma: 11655:13591 FAQ - General (+ Products / App & Data / Orders & Shipping / Warranty & Support). Generated by tools/gen_faq.py -->
<section class="section theme-dark subpage-hero" aria-labelledby="faq-title">
  <div class="container subpage-hero__inner">
    <div class="subpage-hero__copy">
      <h1 id="faq-title" class="t-h2">Frequently asked questions</h1>
      <p class="t-body">Still have questions? We’re here to help you.</p>
      <a class="btn btn--glass btn--xs" href="#contact">Contact us</a>
    </div>
  </div>
</section>
<section class="section subpage-body" aria-label="Questions by topic">
  <div class="subpage-card faq-card-page" data-tabs>
    <div class="faq-tabs" role="tablist" aria-label="FAQ topics" aria-orientation="vertical">
      {"".join(tabs)}
    </div>
{chr(10).join(panels)}
  </div>
</section>
'''
    OUT.write_text(html, encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    build()
