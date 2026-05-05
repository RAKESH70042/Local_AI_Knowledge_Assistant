"""
synth_data.py
-------------
Generates synthetic knowledge base documents based on real company content:
  - SharePoint basics
  - Fennex overview
  - FloCard introduction
  - Kid Care overview

Run:
    python synth_data.py

Output:
    data/docs/synth_*.txt  — generated knowledge documents
    data/docs/synth_*.meta.json — metadata for each document
"""

import os
import json
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("data/docs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Helper ────────────────────────────────────────────────────────────────────

def save_doc(filename: str, content: str, metadata: dict):
    txt_path  = OUTPUT_DIR / filename
    meta_path = OUTPUT_DIR / filename.replace(".txt", ".meta.json")

    txt_path.write_text(content.strip(), encoding="utf-8")
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"  ✓ Created: {filename}  ({len(content):,} chars)")


# ── Document 1: SharePoint FAQ ────────────────────────────────────────────────

def gen_sharepoint_faq():
    content = """
SharePoint Basics — Frequently Asked Questions

Q: What is Microsoft SharePoint?
A: Microsoft SharePoint is a web-based platform used by organizations to store, organize, share, and access information securely. It is part of the Microsoft 365 ecosystem and integrates with tools like Word, Excel, Teams, and OneDrive.

Q: Is SharePoint cloud-based?
A: Yes. SharePoint Online is a cloud-based service hosted by Microsoft. Businesses subscribe to a Microsoft 365 plan or the standalone SharePoint Online service instead of installing it on their own servers.

Q: What can employees do with SharePoint?
A: With SharePoint, employees can:
- Build intranet sites and create pages, document libraries, and lists
- Add web parts to customize content
- Show important visuals, news, and updates with team or communication sites
- Discover, follow, and search for sites, files, and people across the company
- Manage daily routines with workflows, forms, and lists
- Sync and store files in the cloud so anyone can securely work together
- Catch up on news on the go with the mobile app

Q: What is a Document Library in SharePoint?
A: A document library provides a secure place to store files where employees can find them easily, work on them together, and access them from any device at any time. Files can be organized in folders and moved by dragging and dropping.

Q: What is a SharePoint Site?
A: A SharePoint site is a web-based, secure workspace within Microsoft 365 used to store, organize, share, and collaborate on information from any device. It acts as a central hub for teams to co-author documents, manage lists, and share news.

Q: What are SharePoint Workflows?
A: SharePoint workflows are pre-programmed mini applications that streamline and automate business processes such as collecting signatures, feedback, approvals, or tracking the status of routine procedures.

Examples of workflows:
- Document approval flows
- Leave request approvals
- Notification triggers

Q: What are real enterprise use cases for SharePoint?

1. Employee Onboarding System
   New hire documents are stored in a library. An automated workflow sends tasks to HR and the manager, resulting in faster and structured onboarding.

2. Document Approval Workflow
   Uploading a document triggers an approval flow. The manager reviews and approves or rejects it. Notifications are sent automatically, eliminating email chaos.

3. Project Collaboration Hub
   Each project gets its own SharePoint site with files, timelines, and updates in one place. Team members collaborate in real-time for improved coordination.

Q: Which devices support SharePoint?
A: SharePoint works on PC, Mac, and mobile devices.

Q: How does SharePoint integrate with Microsoft 365?
A: SharePoint integrates natively with Word, Excel, Teams, and OneDrive, making it easy to co-author documents and share information across the Microsoft ecosystem.
"""
    metadata = {
        "title": "SharePoint Basics FAQ",
        "tags": ["sharepoint", "microsoft365", "collaboration", "intranet", "workflow"],
        "type": "faq",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "source": "Basics of SharePoint.odt"
    }
    save_doc("synth_sharepoint_faq.txt", content, metadata)


# ── Document 2: Fennex Company Overview ───────────────────────────────────────

def gen_fennex_overview():
    content = """
Fennex — Company Overview and Product Guide

About Fennex
Fennex is a UK-based, award-winning industrial software company specializing in cloud-based digital solutions for safety, risk management, and compliance within high-risk industries, particularly energy and renewables.

Founded: 2016
Headquarters: Aberdeen, UK
Focus: Offshore oil and gas, wind energy sectors
Approach: AI-powered tools and real-time data analytics to transform manual safety processes into automated digital workflows

Mission Statement (Adrian Brown, Founder and Managing Director):
"At Fennex, we set out to reimagine how complex offshore operations manage safety, risk and compliance. With deep industry experience and a passion for innovation, our team is committed to delivering technology that doesn't just digitize processes — but improves outcomes."

Goal:
Fennex creates data-driven solutions to make industries safer, more efficient, and smarter.

Solution Areas:
1. Health and Safety
2. Risk Management
3. Compliance and Assurance

Products Provided by Fennex:

1. FennexSafe™
FennexSafe simplifies environmental, health, safety and assurance processes in one digital suite, reducing complexity, minimizing risk, and fostering a proactive safety culture across the organization.

2. BBSS™ (Behavior-Based Safety Solution)
BBSS is a data-driven, AI-powered safety solution that transforms safety observation data into real-time intelligence for early risk detection, improved reporting, and proactive decision making to prevent incidents.

3. Risk Management Tool
A cloud-based platform that unifies all types of organizational risk into a single, intelligent system — enabling consistent, real-time, and compliant risk governance across high-risk and regulated industries.

4. Audit and Inspections
Moves organizations from reactive, inconsistent assurance practices to proactive, transparent, and efficient compliance management.

5. AI Predictive Safety
An AI-powered predictive safety tool that transforms data into foresight — anticipating incidents, enabling early intervention, and protecting before risks escalate.
Tagline: Predict. Prevent. Protect.

6. WindSafe™
A unified, data-driven platform that empowers wind operators with full visibility and control across HSEQ (Health, Safety, Environment, Quality), enabling safer operations, stronger compliance, and better outcomes.

Relationship with 366Pi Technologies:
Fennex is an important client for 366Pi Technologies. 366Pi works with Fennex on software development, system management, updates, scaling, and security.
"""
    metadata = {
        "title": "Fennex Company Overview",
        "tags": ["fennex", "safety", "risk management", "compliance", "offshore", "AI", "366pi"],
        "type": "company_overview",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "source": "Fennex Overview.odt"
    }
    save_doc("synth_fennex_overview.txt", content, metadata)


# ── Document 3: FloCard Product Guide ────────────────────────────────────────

def gen_flocard_guide():
    content = """
FloCard — Product Guide and Use Cases

What is FloCard?
FloCard is a digital visiting card product built through continuous evolution and real-world learning. Although conceived in 2018, its true value emerged during the Covid pandemic, which highlighted the need for contactless, digital, and sustainable solutions.

Problem FloCard Solves:
FloCard addresses the overuse of plastic and paper materials used in traditional visiting cards and identity sharing. Physical cards contribute to environmental waste and are inefficient to manage and update.

Solution:
FloCard provides a one-click digital solution that replaces physical cards with eco-friendly, contactless sharing — helping individuals, organizations, and governments move toward the goals of SDG 2030.

By reducing dependency on plastic and paper, FloCard supports sustainable growth while making information sharing faster, cleaner, and more efficient.

Primary Users:
- Company employees
- Intern candidates
- Organizations seeking sustainable identity solutions

Company Goals aligned with UN SDGs:
FloCard's mission aligns with the United Nations Sustainable Development Goals (SDG 2030), including:
- No Poverty
- Zero Hunger
- Good Health and Well-being
- Quality Education
- Gender Equality
- Clean Water and Sanitation
- Affordable and Clean Energy
- Decent Work and Economic Growth
- Industry, Innovation and Infrastructure
- Reduced Inequalities
- Sustainable Cities and Communities
- Responsible Consumption and Production
- Climate Action
- Life Below Water
- Life on Land
- Peace, Justice and Strong Institutions
- Partnerships for the Goals

Tree Planters Initiative:
Tree Planters is an environmental initiative connected to FloCard's sustainability mission.
- Helps increase green cover and supports a healthier environment
- Contributes to sustainability by planting trees and reducing carbon impact
- Plays a key role in restoring nature and promoting ecological balance

Key Benefits of FloCard:
- Eco-friendly: eliminates plastic and paper waste
- Contactless: safe and hygienic sharing
- Instant updates: no need to reprint cards
- Digital: accessible on any device
- Sustainable: supports SDG 2030 goals
"""
    metadata = {
        "title": "FloCard Product Guide",
        "tags": ["flocard", "digital card", "sustainability", "SDG", "contactless", "eco-friendly"],
        "type": "product_guide",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "source": "FloCard Intro.odt"
    }
    save_doc("synth_flocard_guide.txt", content, metadata)


# ── Document 4: Kid Care Overview ────────────────────────────────────────────

def gen_kidcare_overview():
    content = """
Kid Care — Platform Overview and Module Guide

What is Kid Care?
Kid Care is a healthcare-focused platform designed specifically for newborns and children, addressing critical areas such as growth, nutrition, development, and common illnesses.

It connects parents, caregivers, and pediatricians into one unified system to ensure continuous and efficient child healthcare management.

Problems Kid Care Solves:
- Child healthcare is often fragmented across clinics, records, and communication channels
- Parents struggle with tracking health, appointments, and medical history
- Lack of real-time communication between parents and doctors
- Difficulty in managing nutrition, growth, and developmental monitoring
- Limited access to organized pediatric care and guidance in one place

Solution:
Kid Care provides a centralized digital platform that simplifies child healthcare by integrating:
- Health tracking and medical records
- Appointment scheduling and follow-ups
- Doctor-parent communication
- Nutritional suggestions and mental health choices tailored to the child's needs
- Medical records management, billing, payments, and insurance information

Modules in Kid Care:

1. Parent Module
   - Manage child health: symptoms, tracking, teleconsultation
   - Book appointments and communicate with doctors
   - Ensures that caring for a child is as seamless as possible

2. Caregiver Module
   Designed for healthcare professionals involved in childcare:
   - Access patient data and integrate with EHR systems
   - Manage appointments, prescriptions, and treatment plans
   - Engage with children's activities and parent community
   - Track health, recommend tests and procedures, and analyze data for insights
   - Facilitate communication with patients and coordinate emergency responses
   - Handle system upkeep, payment reception, and patient follow-ups

3. Pediatrician Module
   - Access patient information and provide pediatric diagnosis and treatment
   - Offer emergency pediatric care
   - Manage appointments and telemedicine consultations
   - Provide preventive care, nutrition advice, and counseling
   - Track vaccinations and child health analytics
   - Refer patients to specialists when required

Aim of Kid Care:
Kid Care is nurturing growth and wellness from infancy to adolescence. It strives to cultivate a healthier community by providing holistic pediatric care, empowering parents through education, and championing the essential role of nutrition, prevention, and early intervention.

Key Features:
- Unified platform for parents, caregivers, and pediatricians
- Real-time doctor-parent communication
- Vaccination tracking
- Telemedicine consultations
- Nutritional and developmental monitoring
- EHR (Electronic Health Record) integration
- Billing and insurance management
"""
    metadata = {
        "title": "Kid Care Platform Overview",
        "tags": ["kidcare", "healthcare", "pediatrics", "children", "parents", "telemedicine"],
        "type": "product_overview",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "source": "Kid Care – Overview.odt"
    }
    save_doc("synth_kidcare_overview.txt", content, metadata)


# ── Document 5: 366Pi Internal FAQ ───────────────────────────────────────────

def gen_366pi_faq():
    content = """
366Pi Technologies — Internal Knowledge FAQ

Q: What does 366Pi Technologies do?
A: 366Pi Technologies is a software development company that works with clients across multiple industries. Key clients include Fennex (industrial safety software) and products like FloCard (digital cards) and Kid Care (pediatric healthcare platform).

Q: What is our relationship with Fennex?
A: Fennex is an important client for 366Pi Technologies. We work with them on software development, system management, updates, scaling, and security. Fennex specializes in cloud-based digital solutions for safety, risk management, and compliance in high-risk industries.

Q: What products does 366Pi work on?
A: 366Pi works on several products including:
- Fennex platform (FennexSafe, BBSS, Risk Management, WindSafe)
- FloCard (digital visiting card solution)
- Kid Care (pediatric healthcare platform)
- SharePoint-based internal tools and workflows

Q: What is SharePoint used for internally?
A: SharePoint is used for document storage, team collaboration, workflows, and project management. Common use cases include employee onboarding, document approval workflows, and project collaboration hubs.

Q: How do we handle document approvals?
A: Document approvals are managed through SharePoint workflows. A document is uploaded, which triggers an approval flow. The manager reviews and approves or rejects it. Notifications are sent automatically.

Q: What is the SDG 2030 initiative related to FloCard?
A: FloCard aligns with the United Nations Sustainable Development Goals (SDG 2030) by replacing plastic and paper visiting cards with eco-friendly digital alternatives. The company also runs the Tree Planters initiative to increase green cover and reduce carbon impact.

Q: What technology stack does Fennex use?
A: Fennex uses AI-powered tools and real-time data analytics. Their platform includes products like BBSS (behavior-based safety solution using AI) and AI Predictive Safety tools that transform data into foresight to prevent incidents.

Q: What modules does Kid Care have?
A: Kid Care has three main modules:
1. Parent Module — health tracking, appointments, teleconsultation
2. Caregiver Module — patient data, EHR integration, prescriptions
3. Pediatrician Module — diagnosis, telemedicine, vaccination tracking

Q: When was Fennex founded?
A: Fennex was founded in 2016 and is headquartered in Aberdeen, UK.

Q: What industries does Fennex serve?
A: Fennex primarily serves the offshore oil and gas and wind energy sectors, focusing on safety, risk management, and compliance in high-risk environments.
"""
    metadata = {
        "title": "366Pi Technologies Internal FAQ",
        "tags": ["366pi", "internal", "faq", "fennex", "flocard", "kidcare", "sharepoint"],
        "type": "internal_faq",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "source": "synthetic"
    }
    save_doc("synth_366pi_faq.txt", content, metadata)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  SYNTHETIC DATA GENERATOR")
    print("  Based on 366Pi company documents")
    print("="*50 + "\n")
    print(f"Output directory: {OUTPUT_DIR.resolve()}\n")

    gen_sharepoint_faq()
    gen_fennex_overview()
    gen_flocard_guide()
    gen_kidcare_overview()
    gen_366pi_faq()

    print(f"\n✅ Generated 5 synthetic documents in: {OUTPUT_DIR.resolve()}")
    print("\nNext step — re-index your documents:")
    print("  python -m core.pipeline index")
    print("="*50 + "\n")