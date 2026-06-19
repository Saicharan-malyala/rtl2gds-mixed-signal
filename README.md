# AI-Assisted Mixed-Signal RTL-to-GDSII Physical Design Flow

![Flow-OpenLane](https://img.shields.io/badge/Flow-OpenLane-blue?style=for-the-badge)
![PDK-SKY130](https://img.shields.io/badge/PDK-SKY130-orange?style=for-the-badge)
![Technology-130nm](https://img.shields.io/badge/Technology-130nm-green?style=for-the-badge)
![Verification-Physical_Design](https://img.shields.io/badge/Focus-Mixed--Signal%20Physical%20Design-purple?style=for-the-badge)
![License-Apache](https://img.shields.io/badge/License-Apache%202.0-yellow?style=for-the-badge)

In this repository, I document how I approach a **mixed-signal RTL-to-GDSII physical design flow** using [OpenLane](https://openlane2.readthedocs.io/), the [SKY130](https://skywater-pdk.readthedocs.io/) Process Design Kit, and supporting open-source tools such as [OpenROAD](https://openroad.readthedocs.io/), [Magic](http://opencircuitdesign.com/magic/), and [KLayout](https://www.klayout.de/).

My intention here is not just to collect files. I want this repository to explain, in a compact and technically meaningful way, **what mixed-signal top-level physical design really involves**, **why it differs from a purely digital flow**, and **how an AI-assisted engineering workflow can still remain disciplined, verifiable, and technically grounded**.

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. What I Mean by a Mixed-Signal RTL-to-GDSII Flow](#2-what-i-mean-by-a-mixed-signal-rtl-to-gdsii-flow)
- [3. Hard Macro Integration: The Three Essential Views](#3-hard-macro-integration-the-three-essential-views)
- [4. Physical Design Flow Overview](#4-physical-design-flow-overview)
- [5. What OpenLane Contributes to This Flow](#5-what-openlane-contributes-to-this-flow)
- [6. Why This Repository Is AI-Assisted](#6-why-this-repository-is-ai-assisted)
- [7. What This Repository Tries to Offer the Reader](#7-what-this-repository-tries-to-offer-the-reader)
- [8. Detailed Implementation Note](#8-detailed-implementation-note)
- [9. Tools and Technology Stack](#9-tools-and-technology-stack)
- [10. Key Mixed-Signal Design Insight](#10-key-mixed-signal-design-insight)
- [11. Acknowledgements](#11-acknowledgements)
- [12. Final Note](#12-final-note)
- [Contact and Discussion](#contact-and-discussion)
  
---

## 1. Introduction

Modern SoC design is rarely purely digital. In practice, digital control logic often has to work together with analog blocks such as multiplexers, PLLs, DACs, ADCs, regulators, and other custom macros. That is where mixed-signal physical design becomes important.

In a standard digital flow, the implementation tools expect synthesizable RTL, standard-cell libraries, and regular placement behavior. In a mixed-signal flow, that assumption changes because the analog portion is usually integrated as a **hard macro**. Its internal transistor-level implementation is not rebuilt by the digital place-and-route flow, but its interface, timing abstraction, and physical boundary still have to be integrated correctly at the top level.

This repository is my compact front-door explanation of that overall idea: from RTL understanding to macro integration, physical implementation, verification, and final layout generation.

---

## 2. What I Mean by a Mixed-Signal RTL-to-GDSII Flow

When I say **mixed-signal RTL-to-GDSII flow**, I mean a physical design flow where:

- the **digital hierarchy** is synthesized and implemented through an automated RTL-to-GDSII toolchain,
- the **analog block** is integrated as a pre-designed hard macro,
- and both worlds are connected through logical, timing, and physical abstractions.

The digital toolchain does **not** need to know the full transistor-level internals of the analog block. What it does need is enough information to:

- compile the top-level design,
- understand the macro boundary and pin interface,
- estimate timing and loading behavior,
- place and route the surrounding digital logic safely,
- and complete verification without breaking signoff requirements.

That separation is one of the most important ideas in mixed-signal top-level integration.

---

## 3. Hard Macro Integration: The Three Essential Views

For a mixed-signal hard macro to be integrated correctly inside a digital physical design flow, I treat it as three coordinated views of the same block:

| View | Purpose | Used By |
|------|---------|---------|
| **Verilog Stub** | Declares the macro ports so synthesis can compile the top-level design | Yosys / RTL flow |
| **LEF Abstract** | Describes macro size, pins, and physical interface for placement and routing | OpenROAD / PnR |
| **Liberty (`.lib`) Model** | Provides timing and electrical behavior for STA | Timing analysis |

This abstraction is what makes it possible to connect analog IP into a largely digital implementation pipeline without flattening or re-implementing the analog layout itself.

Official OpenLane documentation also treats macros as pre-hardened blocks that are integrated into a top-level chip through the required physical and implementation views rather than re-implemented from scratch inside one single flow [Source](https://openlane2.readthedocs.io/en/latest/usage/using_macros.html).

---

## 4. Physical Design Flow Overview

I treat the RTL-to-GDSII path as a sequence of engineering stages, where each stage has its own role and its own failure modes.

<p align="center">
  <img src="https://openlane2.readthedocs.io/en/latest/_images/asic-flow-diagram.webp"
       alt="General ASIC RTL-to-GDSII Flow"
       width="1000">
</p>

<p align="center"><em>General ASIC / RTL-to-GDSII flow illustration</em></p>

**Synthesis** maps RTL into standard cells while preserving the analog macro as a hardened or black-box instance.

**Floorplanning** defines core area, utilization, macro placement intent, and the early physical structure of the design.

**Placement** arranges standard cells around the macro while respecting density, halos, blockages, and routing feasibility.

**Clock Tree Synthesis (CTS)** builds a controlled clock network for sequential logic.

**Routing** completes signal connectivity between digital logic and macro pins through the available routing resources.

**Signoff and verification** then check design-rule correctness, timing behavior, antenna effects, and physical consistency before final layout generation.

*General ASIC / RTL-to-GDSII flow illustration* [Source](https://openlane2.readthedocs.io/en/latest/getting_started/newcomers/index.html)

What makes mixed-signal implementation interesting is that the hardest issues often do not come from RTL alone. They usually appear at the boundaries between abstraction levels: malformed LEF data, inaccessible macro pins, incomplete Liberty information, routing access limitations, macro classification issues, or mismatches across implementation and verification tools.

---

## 5. What OpenLane Contributes to This Flow

OpenLane is important in this repository because it provides an **automated RTL-to-GDSII flow** built on top of multiple open-source tools. That makes it a practical bridge between front-end design intent and back-end physical implementation.

<p align="center">
  <img src="https://antmicro.com/blog/images/openlane-flow.png"
       alt="OpenLane Automated Flow"
       width="1000">
</p>

<p align="center"><em>OpenLane automated RTL-to-GDSII flow</em></p>

OpenLane brings together stages such as synthesis, timing checks, floorplanning, PDN preparation, placement, clock-related implementation, routing, physical checks, and final GDSII generation in a structured automated flow.

For me, that matters because it turns mixed-signal top-level integration into something I can study, debug, refine, and verify in a more systematic way rather than treating the entire backend as a black box.

*OpenLane automated RTL-to-GDSII flow* [Source](https://antmicro.com/blog/2021/10/openlane-asic-build-flow-with-systemverilog-support)

That automation does not remove engineering responsibility. It simply gives me a strong open framework in which I can evaluate floorplanning decisions, macro integration quality, routing behavior, and signoff outcomes with much better visibility.

---

## 6. Why This Repository Is AI-Assisted

I developed and documented this work in an **AI-assisted engineering workflow**.

That does **not** mean AI replaced engineering judgment. What it means is that I used AI assistants to help me:

- interpret unfamiliar tool logs,
- reason about flow failures,
- compare possible fixes,
- refine configuration choices,
- and improve documentation quality while preserving technical meaning.

My actual approach is simple:

**propose → verify → refine → commit**

Whenever I hit a tool issue, I first study the logs, reports, and physical outputs. I then use AI as a reasoning and debugging companion, and finally I validate the result myself through reruns, reports, and layout inspection. I treat AI as a productivity and learning accelerator, not as a substitute for verification.

That distinction matters, especially in physical design, where a suggestion is only useful if it survives real tool behavior.

---

## 7. What This Repository Tries to Offer the Reader

If you are reading this repository for the first time, I want you to understand three things clearly:

1. **What a mixed-signal top-level physical design flow actually involves**
2. **How analog hard macros are integrated into a digital RTL-to-GDSII environment**
3. **How AI can be used responsibly in an engineering workflow without compromising verification discipline**

So this repository is not only about obtaining a final layout. It is also about documenting the path, the assumptions, the abstractions, and the physical-design reasoning behind the flow.

---

## 8. Detailed Implementation Note

The purpose of this main README is to present the repository at a high level.

For the full implementation story — including actual debugging iterations, OpenLane run behavior, macro integration issues, verification observations, and final physical design outcomes — I maintain a separate **Week 1 / Task 1** write-up inside this repository.

That detailed note goes much deeper into:

- the selected mixed-signal design,
- configuration evolution,
- macro LEF / LIB handling,
- placement and routing issues,
- signoff-stage behavior,
- and the exact engineering decisions taken across the flow.

---

## 9. Tools and Technology Stack

The work documented here is centered around the following ecosystem:

- [OpenLane](https://openlane2.readthedocs.io/) — automated RTL-to-GDSII flow  
- [OpenROAD](https://openroad.readthedocs.io/) — physical design engine  
- [SKY130](https://skywater-pdk.readthedocs.io/) — open-source 130nm PDK  
- [Yosys](https://github.com/YosysHQ/yosys) — synthesis  
- [Magic](http://opencircuitdesign.com/magic/) — layout viewing, DRC, and GDS support  
- [KLayout](https://www.klayout.de/) — layout inspection and streamout-related verification  
- [Verilator](https://www.veripool.org/verilator/) — linting / frontend support where applicable  

These tools matter not only because they are open-source, but because they expose the implementation flow in a way that allows deeper understanding of what each stage is actually doing.

---

## 10. Key Mixed-Signal Design Insight

One of the biggest lessons behind this repository is that mixed-signal integration is not just about connecting analog and digital blocks at the schematic level.

It is about making sure that:

- the **logical interface** is understood,
- the **physical interface** is routable,
- the **timing abstraction** is acceptable,
- and the **verification flow** stays consistent across multiple tools.

That is why even a small mixed-signal design can reveal a surprisingly rich physical-design learning curve.

---

## 11. Acknowledgements

I would like to acknowledge:

- **Kunal Ghosh, Co-founder, VSD Corp. Pvt. Ltd**
- the [OpenLane](https://openlane2.readthedocs.io/) and [OpenROAD](https://theopenroadproject.org/) communities
- the [SKY130 PDK documentation](https://skywater-pdk.readthedocs.io/)
- the reference mixed-signal integration work from [`praharshapm/vsdmixedsignalflow`](https://github.com/praharshapm/vsdmixedsignalflow), which helped shape the practical framing of this domain

---

## 12. Final Note

I built this repository to document mixed-signal physical design in a way that stays technically meaningful, implementation-aware, and readable for someone who is trying to understand the flow from the ground up.

If you are coming here as a learner, I hope this repository helps you connect the theory of mixed-signal integration with the realities of open-source physical design tools. If you are coming here with prior background, I hope the AI-assisted methodology and implementation notes still make the documentation worthwhile.



## Contact and Discussion

This repository is part of my ongoing learning journey in mixed-signal physical design and RTL-to-GDSII implementation. Feedback, corrections, and technical discussions are always welcome.

- LinkedIn: https://linkedin.com/in/saicharan-malyala

If you notice an error, have a suggestion, or would like to discuss physical design concepts, please open an Issue or connect with me.
