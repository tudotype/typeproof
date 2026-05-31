#!/usr/bin/env python3
"""Found-in-the-wild lint test — paragraphs scraped from automattic.com.

Pull is from 2026-04-26 and covers: homepage, /about/, /work-with-us/,
/work-with-us/how-we-hire/, automattic.design, /press/.

The goal is to surface what the lint engine would do to real Automattic
prose: clean wins, no-ops, and anything that looks like a false-positive.
"""
from __future__ import annotations

from typeproof import TypographyLinter


# 50 paragraphs scraped from automattic.com on 2026-04-26.
# Verbatim — straight quotes, hyphens, em dashes as encoded in source HTML.
CORPUS: list[str] = [
    # --- Homepage ---
    '"We are much better at writing code than haiku." — Matt Mullenweg, founder of Automattic',
    "We also contribute to a number of non-profit and Open Source projects, like WordPress.org and various mobile applications.",
    "© Automattic Inc., purveyors of fine blogging and site-building services since 2005. Thank you for your time.",

    # --- /about/ ---
    "In a world of tech companies fighting for growth at any cost, imagine one that gives away its most successful product for free—and has been doing it for 20 years.",
    "Whereas an increasing number of tech firms spend their energy locking customers into closed, ever-worsening platforms designed to extract value at any cost (including the customer's right to privacy), picture yourself working at a company that prioritizes and protects our customers' freedom to use all the tools of the open web.",
    "With a founding product so successful, schoolchildren know it by name. A product so ubiquitous, it powers over 40% of all websites. And that's just one of the things we make.",
    "We're the people behind WordPress.com, WooCommerce, Tumblr, Simplenote, Jetpack, Longreads, Day One, Pocket Casts, and more. We believe in making the web a better place, and strive to live by the Automattic Creed. There are 1,450 of us Automatticians in nearly every corner of the globe, speaking 107 different languages.",
    "Enriched by this diversity, we're united by a singular mission: to democratize publishing, commerce, and messaging so anyone with a story can tell it, anyone with a product can sell it, and everyone can manage their communications from a single source.",
    "In short, we help maintain a balance in society, creating and continually refining powerful tools people can use to compete fairly—regardless of income, gender, politics, language, or where in the world they live.",
    "In a time when companies are demanding employees return to the office or lose their jobs, we've been a remote-first company since our founding in 2005.",
    "We value impact, not how much time you put in. Effectiveness over busyness. Quality, not quantity. We firmly believe that work can and should be fun, while also being challenging and providing essential services.",
    "That workers should be trusted by giving them autonomy over the choices they make and the projects they take on. And that makers deserve to see real-world results of their efforts.",
    "We believe in Open Source, and the vast majority of our work is available under the GPL. And we've proven you can build an open-source-driven business—earning half a billion $US in annual revenue!—while providing top shelf, future-friendly services that help our customers build their own businesses, tell their own stories, and manage their work and family lives.",
    "If you're independent, creative, skilled, smart, and looking to do the most meaningful work of your career, on your own turf and your own terms, and with a high-impact footprint improving the lives of millions of people worldwide, you'll love working here.",
    "Sometimes you want to turn Slack handles into face-to-face conversations. Our NoHo, NYC and Mission, SF spaces mean that wherever you usually work from, there's a place you can drop by to collaborate, learn, connect, or just spend some time with Automatticians and friends.",

    # --- /work-with-us/ ---
    "Explore the remote job opportunities at Automattic. Work from anywhere, and make the web a better place for everyone, everywhere. Check out today's open jobs.",
    "We're 1,450 Automatticians in 81 countries speaking 107 languages. We democratize publishing and commerce so anyone with a story can tell it, and anyone with a product can sell it, regardless of income, gender, politics, language, or country.",
    "You submit a formal application for a current job opening, giving us a sense of your communication style. We assess based on criteria that vary depending on the opening and the needs of the team, and pay close attention to your answers — so share as much relevant information as possible!",
    "One of the first steps in the application process is a Slack or Zoom interview. While some roles start with a written interview on Slack, others require Zoom interviews, so we can get to know you better live.",
    "Our jobs involve a paid trial in the application process, which is a short project or set of tasks that will be assessed by our hiring teams. You will have the chance to work on something that's closely aligned with the role you're interviewing for, and tackle a specific, real problem.",
    "Once a candidate successfully completes their trial, many teams require a final interview — typically conducted by an executive leader within the business unit — before proceeding to the offer stage.",
    "At Automattic, we want people to love their work and show respect and empathy to all. We welcome differences and strive to increase participation from traditionally underrepresented groups.",
    "Everyone works from the location they choose, during the hours they choose. We're spread out all over the world. We track about 70 percent of our projects on P2-themed WordPress.com blogs, 25 percent in private chat rooms, and the rest on Slack.",
    "Because of the geographic variance, we're active 24/7. But don't let that worry you. This is not a work-'til-you-drop place. We encourage work-life balance, and care about the work you produce, not the hours you put in.",
    "Since the pandemic, we've focused on smaller groups, division meetups, and so on, that accomplish bonding and coworking on a manageable scale.",
    "In addition to our larger meetups, individual teams meet for five to seven days to brainstorm team-level strategy and bond in locales ranging from Boulder to Buenos Aires, Las Vegas to Lisbon, Montréal to Mexico City, and Vienna to Vietnam.",

    # --- automattic.design ---
    "At Automattic, we transform the web for over a billion people every month by solving problems that matter.",
    "Our passion extends beyond code—we share stories about design, our team, our products, and our process.",
    "From the technologies we build to how we collaborate, open source principles guide everything we do.",
    "We value results over time spent. Our distributed team works across diverse projects spanning product design, UX, brand design, marketing campaigns, themes, and custom site design— with the freedom to work how and when they perform best.",
    "Communication is oxygen. Stay up-to-date with stories about design, the team, our products, interviews and how-to guides from like-minded creative souls.",

    # --- /press/ ---
    "We're happy to answer your questions about Automattic, or about any of our products.",
    "Automattic wants to make the web a better place. Our family includes WordPress.com, Woo, Jetpack, WordPress VIP, Simplenote, Longreads, The Atavist, WPScan, Akismet, Gravatar, Crowdsignal, Cloudup, Tumblr, Day One, Pocket Casts, Newspack, Beeper, and more.",
    "With WordPress.com, you can create beautiful websites and blogs for free and enhance those sites with our premium services.",
    "A fully distributed company, Automattic has more than 1,450 employees working from 81 countries.",
    "Automattic owns and operates WordPress.com, which is a hosted version of the open source WordPress software with added features for security, speed and support.",
    "WordPress is open source software, which is written, maintained, and supported by thousands of independent contributors worldwide.",
    "Automattic is a major contributor to the WordPress open source project.",

    # --- /work-with-us/how-we-hire/ ---
    '"The interview felt more like hanging out and talking with someone you met at a conference about what you do, what processes you use and why, etc. It was friendly and, dare I say, fun."',
    "Automattic builds WordPress.com and other products that democratize publishing, commerce, and communications. We're a globally distributed team working from over 90 countries, united by our passion for open source, great user experiences, and the web's future.",
    "We believe exceptional work comes from autonomy and flexible environments. We pioneered distributed work long before it became widespread, focusing on output rather than hours logged.",
    "We actively seek colleagues from varied backgrounds, recognizing that diverse perspectives enhance our products and make them accessible to a wider audience. We support internal Resource Groups formed by Automatticians who share characteristics or experiences, and we're dedicated to increasing representation from underrepresented groups in tech through our inclusive hiring practices.",
    "Submit your resume and cover letter. We evaluate your skills, experience, and alignment with our culture. Depending on the role, you might see fields to submit a resume, cover letter, and a few application questions. Make sure to dedicate time and effort to all aspects of your application. Our team places strong emphasis on thoughtful cover letters and thorough responses to application questions.",
    "If you've advanced in the hiring process, you'll be invited into our candidate portal, where you'll see and experience the Automattic hiring process. There you can check out team members, and view in a single, central place all the other important content you'll need as the process continues.",
    "Automattic's first application step often includes a Slack Interview—essential for evaluating text communication skills in our distributed company. When preparing: log in early, take time with responses, bring questions, and consider whether this communication style suits you.",
    "Certain Automattic positions require more verbal communication, so we use 30-60 minute Zoom interviews for these roles. During these conversations with recruiters or hiring team members, you'll discuss your experience and career goals.",
    "For some roles, you'll next complete a paid project that simulates actual work. This replaces traditional technical interviews and allows you to demonstrate your abilities in a realistic setting. Engineering applicants complete a code test with an assigned buddy who reviews work and answers questions.",
    "Qualified candidates complete a paid 5-40 hour project using real work to evaluate mutual fit. Your hiring team provides feedback throughout. This hands-on assessment is mandatory for all positions, as we believe actual collaboration best determines compatibility.",
    "After a successful trial, the hiring team submits a recommendation including your profile, feedback, and work summary to the CEO for final approval (taking days to a month). If approved, HR will contact you regarding compensation and start date based on your role and experience.",
    "When applying to Automattic, it's important to research our products and values to ensure a strong alignment with our mission. Showcase relevant projects and contributions that highlight your skills and how they connect to the role you're pursuing. In your cover letter, demonstrate excellent communication skills — clear, thoughtful writing is highly valued here.",
    "Be prepared to discuss how you work independently, manage your time effectively, and stay motivated without direct supervision. Finally, highlight any experience you have with distributed teams or remote work, as collaboration across time zones is a key part of how we operate.",
    '"The more we thought about why some hires succeeded and some didn\'t, the more we recognized that there is no substitute for working alongside someone in the trenches. So we gradually changed our approach."',
]


def show_diff(before: str, after: str, max_inline: int = 240) -> str:
    """Pretty-print only the changed regions of before/after."""
    if before == after:
        return "(no change)"
    # Find first/last differing index
    i = 0
    while i < min(len(before), len(after)) and before[i] == after[i]:
        i += 1
    j_before, j_after = len(before), len(after)
    while j_before > i and j_after > i and before[j_before - 1] == after[j_after - 1]:
        j_before -= 1
        j_after -= 1
    pad = 30
    ctx_start = max(0, i - pad)
    ctx_end_b = min(len(before), j_before + pad)
    ctx_end_a = min(len(after), j_after + pad)
    return (
        f"\n  before: …{before[ctx_start:ctx_end_b]!r}…"
        f"\n  after : …{after[ctx_start:ctx_end_a]!r}…"
    )


def main() -> None:
    linter = TypographyLinter(language="en-US", register="editorial")

    no_change = []
    changed = []
    for idx, para in enumerate(CORPUS, 1):
        result = linter.lint(para)
        if result.text == para:
            no_change.append((idx, para))
        else:
            changed.append((idx, para, result))

    print(f"Total paragraphs: {len(CORPUS)}")
    print(f"  No change:      {len(no_change)}")
    print(f"  Changed:        {len(changed)}")
    print()
    print("=" * 70)
    print("CHANGED PARAGRAPHS")
    print("=" * 70)
    for idx, original, result in changed:
        rules = sorted({c.rule for c in result.corrections})
        print(f"\n[{idx}] rules: {', '.join(rules)} ({len(result.corrections)} edits)")
        print(show_diff(original, result.text))

    print()
    print("=" * 70)
    print("RULE FREQUENCY (across all changed paragraphs)")
    print("=" * 70)
    rule_counts: dict[str, int] = {}
    for _, _, result in changed:
        for c in result.corrections:
            rule_counts[c.rule] = rule_counts.get(c.rule, 0) + 1
    for rule, count in sorted(rule_counts.items(), key=lambda x: -x[1]):
        print(f"  {rule:35s} {count}")


if __name__ == "__main__":
    main()
