"""
================================================================================
Author: Nishitha
Role: Advanced RAG Ingestion Engineering
Created: 2026-05-18
Description: Generates mock correspondence files (emails/letters) for testing 
             the dedicated Domain Correspondence Chunker (Day 6 task).
             Uses pseudo names (Ganga, Yamuna, Simhadri) and pseudo company (Energy Kernel).
================================================================================
"""
import os

def create_mock_correspondence():
    target_dir = "data/correspondence"
    os.makedirs(target_dir, exist_ok=True)
    
    letters = [
        {
            "filename": "let_001_ohe_catenary_ncr_Nishitha.txt",
            "content": """Ref: EK/OHE/2026/089
Date: 2026-05-10
From: Ganga, Chief Project Engineer, Metro Project Authority
To: Yamuna, Senior Infrastructure Lead, Energy Kernel
Subject: NCR-0051 Corrective Action on OHE Catenary Hanger Damage

Dear Yamuna,

Following the recent quality audit at Platform Edge of Station C, we observed severe structural damage to the OHE catenary hanger assembly (refer to NCR-0051). This issue represents a major safety hazard and must be resolved within 48 hours to prevent dynamic load testing delays.

Please submit the material test certificates and torque checking sheets for the replaced hanger clamp assemblies before energization. We cannot authorize Stage 2 tunnel boring machine operations adjacent to this sector until this Non-Conformance is closed.

Sincerely,
Ganga
Chief Project Engineer
"""
        },
        {
            "filename": "let_002_ballastless_track_curing_Nishitha.txt",
            "content": """Ref: EK/TRACK/2026/102
Date: 2026-05-12
From: Yamuna, Senior Infrastructure Lead, Energy Kernel
To: Ganga, Chief Project Engineer, Metro Project Authority
Subject: Ballastless Track Slab Curing temperature and Moisture Control

Dear Sir,

With reference to the joint site inspection on 2026-05-11 regarding the grout separation in the ballastless track slab near the tunnel portal (NCR-0052), we have implemented strict moisture control measures.

Hourly monitoring of the track slab concrete temperature is now active. The moist curing blanket will remain saturated for 14 continuous days as specified in the technical specification manual. Rework is not required as core compression tests confirm structural compliance.

Warm regards,
Yamuna
Senior Infrastructure Lead, Energy Kernel
"""
        },
        {
            "filename": "let_003_tbm_shield_documentation_Nishitha.txt",
            "content": """Ref: EK/TBM/2026/044
Date: 2026-05-13
From: Simhadri, Quality Assurance Lead, Energy Kernel
To: Joint Venture Construction Partners, Metro Line 3
Subject: NCR-0053 Documentation for TBM Shield Locking Mechanism

To Whom It May Concern,

We are issuing this formal notice regarding the incomplete documentation of the TBM (Tunnel Boring Machine) shield locking mechanism. Although the physical alignment has been validated, the inspection sheets do not carry the certified signature of the safety engineer.

Please submit the verified torque checks and pressure gauge logs for the cutterhead hydraulics immediately. Spoil disposal records must also be appended to ensure compliance with the environmental protection clearance.

Best regards,
Simhadri
Quality Assurance Lead, Energy Kernel
"""
        },
        {
            "filename": "let_004_station_cavern_seepage_Nishitha.txt",
            "content": """Ref: EK/CIVIL/2026/211
Date: 2026-05-14
From: Ganga, Resident Engineer, Energy Kernel
To: Simhadri, Waterproofing Subcontractor
Subject: NCR-0056 Active Water Seepage in Station Cavern Ceiling

Dear Sirs,

Active water ingress has been detected in the concrete segment joints of the station cavern ceiling (reference NCR-0056). This seepage is directly impacting the installation of cable trays and fire alarm wiring.

You are instructed to execute high-pressure polyurethane grouting in all affected segment joints by the end of the shift. All payment certificates for the underground lining segment will be withheld until the seepage is completely arrested.

Sincerely,
Ganga
Resident Engineer, Energy Kernel
"""
        },
        {
            "filename": "let_005_joint_alignment_track_Nishitha.txt",
            "content": """Ref: EK/TRACK/2026/145
Date: 2026-05-15
From: Yamuna, Track Alignment Inspector, Energy Kernel
To: Ganga, Operations Manager, Metro Project Authority
Subject: NCR-0054 Grout Joint Alignment Rectification

Dear Sir,

We have completed the correction of the joint alignment between the track slab segments near the depot portal (referred to in NCR-0054).

The transition zone gradient has been adjusted to meet the 1:1000 slope requirement, and torque checks on the anchor bolts have been verified. The track slab surfaces are now fully cured and ready for permanent OHE catenary pole foundations.

Sincerely,
Yamuna
Track Alignment Inspector, Energy Kernel
"""
        }
    ]
    
    for letter in letters:
        file_path = os.path.join(target_dir, letter["filename"])
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(letter["content"].strip())
        print(f"[CREATED] {file_path}")

if __name__ == "__main__":
    create_mock_correspondence()
