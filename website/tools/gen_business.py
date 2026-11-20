#!/usr/bin/env python3
"""Generate the three For Business pages from one template.
Figma: 11654:13647 (Providers), 11654:13937 (Insurance), 11654:14848 (Distributor).
Copy comes from the Figma frames; edit the PAGES data, then run tools/build.py.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "src" / "pages"

QUOTE = ("You can’t just rely on annual visits. SeeMyHealth gives us tools to guide daily habits "
         "and intervene earlier when it matters most.")

PAGES = {
    "business-providers": dict(
        figma="11654:13647", title="SeeMyHealth for Providers",
        desc="Bridge gaps between visits, provide more personalized care, and improve health across patient populations.",
        hero_img="biz-providers-hero", hero_h="Insights that advance healthcare",
        hero_p="Bridge gaps between visits, provide more personalized care, and improve health across patient populations.",
        cta_label="Become a partner", logos=True,
        vp_title="Smarter insights for more personalized",
        vp_cards=dict(left=("vp-left", False), center=("vp-center", False), right=("vp-right", False)),
        vp_center=("Bridging the clinical gap", "Monitor patient health daily to ensure treatment remains effective between visits with continuous, non-invasive biological data monitoring."),
        vp_right=("Data-Driven Wellness Insights", "Convert complex raw metrics into clear, actionable reports for more precise adjustments to patient recovery and wellness plans."),
        seg_bg=("segments-bg", "raw"), seg_kicker="Target Segments",
        seg_h="Tailored solutions for every health practitioner",
        seg_p="Empower your healthcare practice by integrating precise biological insights into your daily patient management for better, long-term data-driven clinical outcomes",
        seg_cards=[
            ("icon-neurology", "Mental Health Therapists", "Monitor sleep and stress data to understand physiological impacts of mental wellness on your patients’ daily lives with precise metrics."),
            ("icon-grocery", "Nutritionists and Dietitians", "Track hydration and body composition in real-time to adjust nutritional goals and metabolic plans with absolute and data-driven clinical precision."),
            ("icon-avg-time", "Performance Health Coaches", "Follow daily activity and heart rate variability to optimize training loads and prevent burnout for peak client performance and recovery."),
            ("STETHOSCOPE", "Functional Medicine Doctors", "Integrate blood pressure and vital signs into a holistic view of systemic health for more effective and proactive root-cause interventions."),
            ("icon-hospital", "Modern Wellness Clinics", "Manage multiple client profiles through our professional dashboard to provide a premium, data-driven experience for all your valued clinic members."),
        ],
        ways_title="Ways to use SeeMyHealth",
        ways=[
            ("Monitor Lifestyle Habits", "Track daily activities and routine changes to ensure consistent long-term healthy habits."),
            ("Optimize Nutritional Programs", "Use smart scale data to adjust plans for effective weight management."),
            ("Enhance Recovery Coaching", "Analyze heart rate variability to balance patient stress levels and recovery needs."),
            ("Improve Sleep Optimization", "Monitor deep sleep cycles daily to create personalized rest and recovery strategies."),
            ("Early Risk Detection Monitoring", "Identify subtle biological changes early to prevent potential chronic health risks."),
            ("Track Daily Hydration", "Monitor water intake through smart flasks to maintain optimal daily bodily functions."),
        ],
        eco_title="Our Ecosystem", roi=None,
        cta_img="biz-cta-family", cta_h="The future of health, built together",
    ),
    "business-insurance": dict(
        figma="11654:13937", title="SeeMyHealth for Insurance",
        desc="Give your teams the real-world health insights needed to price risk and prevent costly claims.",
        hero_img="ins-hero", hero_h="Smarter coverage starts with data",
        hero_p="Give your teams the real-world health insights needed to price risk and prevent costly claims.",
        cta_label="Become a partner", logos=True,
        vp_title="Turning industry friction into opportunity",
        vp_cards=dict(left=("ins-vp-left", True), center=("ins-vp-center", True), right=("ins-vp-right", True)),
        vp_center=("Rising claims costs", "Chronic disease and reactive care models are pushing claims costs higher each year — without a data layer to intervene earlier, the trend continues."),
        vp_right=("Limited preventive data", "Underwriting still relies on one-time medicals and self-reported forms. The gaps between those snapshots are where the most critical risk goes undetected."),
        seg_bg=("ins-support-bg", "full"), seg_kicker="How We Support Insurers",
        seg_h="Tailored solutions for every insurance provider",
        seg_p="SeeMyHealth gives insurers the tools to move from reactive coverage to proactive, data-driven risk management.",
        seg_cards=[
            ("icon-clarify", "Stratify risk with precision", "Continuous biometric data lets insurers build dynamic risk profiles — updated in real time, not just at renewal."),
            ("icon-contactless", "Surface preventive insights", "Early warning signals appear in the data long before they become the conditions that drive claims."),
            ("icon-blood-pressure", "Monitor chronic conditions", "Continuous monitoring provides the longitudinal data needed to support timely intervention for at-risk policyholders."),
            ("icon-mindfulness", "Power behavioral incentive programs", "Sleep, hydration, and activity data gives insurers the foundation to build wellness programs that prove their impact."),
            ("icon-person-shield", "Optimize claims assessment", "Objective health data helps claims teams validate submissions with greater confidence and surface inconsistencies earlier."),
        ],
        ways_title="Built for Every Line of Insurance",
        ways=[
            ("Health Insurance", "Shift coverage from reactive claims toward proactive, data-backed population health management programs."),
            ("Life Insurance", "Continuous biometric tracking replaces one-time medicals for more accurate mortality risk assessment."),
            ("Corporate &amp; Group Benefits", "Give employers measurable insight into workforce health risks and wellness program effectiveness."),
            ("Critical Illness Insurance", "Surface early biometric warning signs that inform smarter critical illness underwriting decisions."),
            ("Disability Insurance", "Track recovery trends and return-to-work readiness with objective, continuous health monitoring data."),
            ("Reinsurance", "Support reinsurers with longitudinal health data for more accurate portfolio risk assessment."),
        ],
        eco_title="Our Ecosystem",
        roi=dict(title="ROI &amp; Business Impact", img="ins-roi", items=[
            ("Reduced Loss Ratio", "Early intervention data reduces claim frequency and severity across your entire portfolio."),
            ("Sharper Risk Segmentation", None), ("Higher Policyholder Lifetime Value", None),
            ("Stronger ESG &amp; Regulatory Positioning", None)]),
        cta_img="ins-cta", cta_h="The future of risk, built together",
    ),
    "business-distributor": dict(
        figma="11654:14848", title="Become a SeeMyHealth Distributor",
        desc="Partner with a fast-growing health tech brand and bring meaningful value to your market.",
        hero_img="dist-hero", hero_h="Bring SeeMyHealth to your market",
        hero_p="Partner with a fast-growing health tech brand and bring meaningful value to your market.",
        cta_label="Become a distributor", logos=False,
        vp_title="Why distribute SeeMyHealth",
        vp_cards=dict(left=("dist-vp-left", True), center=("dist-vp-center", True), right=("dist-vp-right", True)),
        vp_center=("A complete ecosystem, not just a device", "Most wearable brands sell one product. SeeMyHealth offers a full, connected ecosystem — Ring One, Smart Scale, BP Monitor, and Smart Flask — giving distributors a broader range to place and a stronger story to tell."),
        vp_right=("Broad market appeal", "SeeMyHealth is designed for everyone from everyday wellness seekers to athletes, healthcare patients, and corporate wellness programs — which means more channels, more customers, and more opportunity for your business."),
        seg_bg=("dist-who-bg", "full"), seg_kicker="Who We’re Looking For",
        seg_h="We're looking for partners who mean It",
        seg_p="We don't work with distributors — we work with partners. The best fit is someone who understands their market, believes in what they're selling, and wants to build something long-term.",
        seg_cards=[
            ("icon-storefront", "Retail &amp; E-Commerce", "Electronics retailers, health and wellness stores, pharmacies, and online marketplace operators looking to add a high-demand, high-differentiation product to their catalogue."),
            ("icon-hospital-2", "Healthcare Distributors", "Medical device and health equipment distributors with established relationships across clinics, hospitals, rehabilitation centers, and specialist practices."),
            ("icon-menstrual", "Corporate Wellness Providers", "Companies that design and deliver employee wellness programs, benefits platforms, or occupational health services — and are looking for hardware to anchor their offering."),
            ("icon-store", "Regional Distributors", "Operators with strong local or regional market knowledge seeking exclusive or semi-exclusive distribution rights to represent SeeMyHealth within a defined territory."),
        ],
        ways_title="What You Get",
        ways=[
            ("Competitive margins", "Our wholesale pricing is structured to give distributors meaningful margin at both standard and volume tiers — with incentive programs for partners who grow with us."),
            ("Dedicated account management", "Every SeeMyHealth distribution partner gets a dedicated account manager — a single point of contact for orders, support, escalations, and strategic planning."),
            ("Ready-to-use marketing assets", "From product photography and brand guidelines to sales decks and digital ad creatives, we provide a full library of co-brandable materials ready to deploy in your market."),
            ("Product training &amp; certification", "Your sales team will receive structured onboarding, product knowledge training, and access to our certification program — so they can speak confidently about what they're selling."),
            ("Early access to new products", "Distribution partners get priority notification and early access to new product launches — including the upcoming SeeMyHealth Glucometer — before they're available to the general market."),
            ("Co-marketing opportunities", "For high-performing partners, we offer joint campaign support, co-branded activations, and the opportunity to be featured as a certified SeeMyHealth distribution partner across our channels."),
        ],
        eco_title="What you’ll distribute",
        roi=dict(title="Three steps to getting started", img="dist-steps", items=[
            ("Apply", "Fill out our distributor application form. Tell us about your business, your sales channels, and the market you serve. Applications are reviewed within 5 business days."),
            ("Connect", None), ("Launch", None)]),
        cta_img="dist-cta", cta_h="Ready to grow together?",
    ),
}

STETH = ('<span class="steth" aria-hidden="true"><img src="{{img:steth-base}}" alt="">'
         '<img style="inset: 54.69% 20.31% 35.94% 70.31%" src="{{img:steth-v0}}" alt="">'
         '<img style="inset: 44.38% 10% 25.63% 60%" src="{{img:steth-v1}}" alt="">'
         '<img style="inset: 50.63% 22.5% 10% 31.88%" src="{{img:steth-v2}}" alt="">'
         '<img style="inset: 10% 41.25% 44.37% 10%" src="{{img:steth-v3}}" alt=""></span>')


def vp_card(pos, img, is_slice):
    cls = f"vp-card vp-card--{pos}" + (" vp-card--slice" if is_slice else "")
    return f'<figure class="abs {cls}"><img src="{{{{img:{img}}}}}" alt="" loading="lazy"></figure>'


def page(route, d):
    r = route
    out = [f'<!-- meta title="{d["title"]} | SeeMyHealth" description="{d["desc"]}" nav="dark" -->',
           f'<!-- figma: {d["figma"]} (generated by tools/gen_business.py — edit there) -->', ""]
    # Hero
    logos = ""
    if d["logos"]:
        logos = ('\n    <p class="abs t-body biz-hero__trusted">Trusted by top organizations</p>'
                 '\n    <div class="abs biz-hero__logos" role="img" aria-label="Partner organization logos"></div>')
    out.append(f'''<!-- Hero - 20 -->
<section class="section theme-dark biz-hero" aria-labelledby="{r}-hero-title">
  <img class="bg-cover" src="{{{{img:{d["hero_img"]}}}}}" alt="" fetchpriority="high">
  <div class="shade shade--20" aria-hidden="true"></div>
  <div class="canvas biz-hero__canvas">
    <div class="abs biz-hero__copy">
      <h1 id="{r}-hero-title" class="t-h1">{d["hero_h"]}</h1>
      <p class="t-body biz-hero__lede">{d["hero_p"]}</p>
      <a class="btn btn--glass" href="#contact">{d["cta_label"]}</a>
    </div>{logos}
  </div>
</section>
''')
    # Value proposition slider
    c = d["vp_cards"]
    out.append(f'''<!-- Value Proposition (slider, first state) -->
<section class="section theme-light vp" aria-labelledby="{r}-vp-title">
  <div class="canvas vp__canvas">
    <h2 id="{r}-vp-title" class="abs t-h3 t-center vp__title">{d["vp_title"]}</h2>
    {vp_card("left", *c["left"])}
    {vp_card("center", *c["center"])}
    {vp_card("right", *c["right"])}
    <div class="abs vp__text vp__text--center"><h3 class="t-h6">{d["vp_center"][0]}</h3><p class="t-body">{d["vp_center"][1]}</p></div>
    <div class="abs vp__text vp__text--right" aria-hidden="true"><h3 class="t-h6">{d["vp_right"][0]}</h3><p class="t-body">{d["vp_right"][1]}</p></div>
    <div class="abs vp__controls">{{{{> slider-controls-white}}}}</div>
  </div>
</section>
''')
    # Segments
    bg, mode = d["seg_bg"]
    bgcls = "seg__bg--raw" if mode == "raw" else "bg-cover"
    cards = []
    for icon, h, p in d["seg_cards"]:
        ic = STETH if icon == "STETHOSCOPE" else f'<img src="{{{{img:{icon}}}}}" alt="">'
        cards.append(f'      <li class="glass seg-card"><span class="seg-card__icon">{ic}</span><h3 class="t-xl">{h}</h3><p class="t-xs">{p}</p></li>')
    n = len(d["seg_cards"])
    out.append(f'''<!-- Segments (dark, slider first state) -->
<section class="section theme-dark seg" aria-labelledby="{r}-seg-title">
  <img class="{bgcls}" src="{{{{img:{bg}}}}}" alt="" loading="lazy">
  <div class="seg__shade" aria-hidden="true"></div>
  <div class="shade-bottom" style="--h: 45.0625rem; --a: 0.7" aria-hidden="true"></div>
  <div class="canvas seg__canvas">
    <p class="abs t-md seg__kicker">{d["seg_kicker"]}</p>
    <h2 id="{r}-seg-title" class="abs t-h2 seg__title">{d["seg_h"]}</h2>
    <p class="abs t-body seg__lede">{d["seg_p"]}</p>
    <div class="abs seg__bar t-body"><span>01 <span class="t-muted-dark">— 0{n if n == 5 else 5}</span></span><span class="seg__nav"><span class="t-muted-dark">Prev</span><span>/</span><span>Next</span></span></div>
    <ul class="abs seg__cards">
{chr(10).join(cards)}
    </ul>
  </div>
</section>
''')
    # Ways grid
    ways = "\n".join(f'      <li><h3 class="t-xl">{h}</h3><p class="t-xs">{p}</p></li>' for h, p in d["ways"])
    out.append(f'''<!-- Value Proposition (grid) -->
<section class="section theme-light ways{' ways--tall' if route == 'business-distributor' else ''}" aria-labelledby="{r}-ways-title">
  <div class="container ways__inner">
    <h2 id="{r}-ways-title" class="eyebrow">{d["ways_title"]}</h2>
    <ul class="ways__grid">
{ways}
    </ul>
  </div>
</section>
''')
    # Ecosystem
    out.append(f'''<!-- Our Ecosystem -->
<section class="section theme-light eco" aria-labelledby="{r}-eco-title">
  <div class="container eco__inner">
    <div class="eco__head"><h2 id="{r}-eco-title" class="t-h3">{d["eco_title"]}</h2>
      <div class="slider-arrows"><button class="round-btn eco__arrow" type="button" aria-label="Previous"><img src="{{{{img:icon-arrow-left-dark}}}}" alt=""></button><button class="round-btn eco__arrow" type="button" aria-label="Next"><img src="{{{{img:icon-arrow-right-dark}}}}" alt=""></button></div></div>
    {{{{> ecosystem-cards}}}}
  </div>
</section>
''')
    # Metrics
    out.append(f'''<!-- Health & wellness metrics -->
<section class="section theme-dark metrics" aria-labelledby="{r}-metrics-title">
  <img class="metrics__mesh" src="{{{{img:mesh-brown}}}}" alt="" aria-hidden="true" loading="lazy">
  {{{{> metrics-body}}}}
</section>
''')
    # ROI
    if d["roi"]:
        roi = d["roi"]
        items = []
        for i, (h, p) in enumerate(roi["items"], 1):
            if p:
                items.append(f'      <li class="roi-item is-active"><span class="roi-item__track" aria-hidden="true"><span></span></span><div><h3 class="t-lg">{h}</h3><p class="t-body t-faint-40">{p}</p></div><span class="t-body roi-item__num">0{i}</span></li>')
            else:
                items.append(f'      <li class="roi-item"><img class="roi-item__icon" src="{{{{img:icon-dot-ring}}}}" alt=""><div><h3 class="t-lg">{h}</h3></div><span class="t-body roi-item__num">0{i}</span></li>')
        out.append(f'''<!-- ROI & Business Impact -->
<section class="section theme-light roi" aria-labelledby="{r}-roi-title">
  <div class="canvas roi__canvas">
    <h2 id="{r}-roi-title" class="abs t-h2 roi__title">{roi["title"]}</h2>
    <ol class="abs roi__list">
{chr(10).join(items)}
    </ol>
    <figure class="abs roi__img"><img src="{{{{img:{roi["img"]}}}}}" alt="" loading="lazy"></figure>
  </div>
</section>
''')
    # CTA
    out.append(f'''<!-- Become a Partner_Final CTA -->
<section class="section theme-dark final-cta" aria-labelledby="{r}-cta-title">
  <img class="bg-cover" src="{{{{img:{d["cta_img"]}}}}}" alt="" loading="lazy">
  <div class="shade" style="background: rgb(0 0 0 / 0.25)" aria-hidden="true"></div>
  <div class="shade-bottom" style="--h: 32.5rem; --a: 0.7" aria-hidden="true"></div>
  <div class="canvas final-cta__canvas">
    <div class="abs final-cta__copy final-cta__copy--biz">
      <h2 id="{r}-cta-title" class="t-h2">{d["cta_h"]}</h2>
      <a class="btn btn--glass" href="#contact">{d["cta_label"]}</a>
    </div>
  </div>
</section>
''')
    return "\n".join(out)


if __name__ == "__main__":
    for route, d in PAGES.items():
        (OUT / f"{route}.html").write_text(page(route, d), encoding="utf-8")
        print("wrote", route)
