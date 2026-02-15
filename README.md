# Lab 1: Problem Framing & Agentic Architecture

## Overview
This repository contains the work for **Lab 1: Problem Framing & Agentic Architecture**, focusing on strategic planning, system design, and environment readiness. The lab moves beyond a simple chatbot and explores a high-impact Agentic Use Case using the **LangGraph framework**.

---

## Problem Statement
The objective is to design an AI agent that can **perceive, reason, and execute** multi-step actions in a business process that cannot be solved with a single LLM response.  

**Selected Industry Vertical:** E-commerce / Retail Analytics  
**Bottleneck:** Manual tracking and analysis of high-volume order data across multiple sources, including order statuses, payments, and refunds. The process is slow, error-prone, and difficult to scale.

---

## User Personas
- **Operations Manager:** Needs real-time insights into order statuses and customer refunds to optimize operations.
- **Data Analyst:** Requires consolidated data from multiple sources for reporting and trend analysis.
- **Customer Service Lead:** Wants automated alerts on failed or refunded orders to proactively manage customer experience.

---

## Success Metrics
- **Data Coverage:** Agent successfully aggregates all relevant order data from multiple sources.  
- **Query Accuracy:** Ability to answer complex queries about order statuses, refunds, and payment methods.  
- **Execution Efficiency:** Reduction in manual intervention for reporting and notifications.  
- **Response Time:** Average response time for queries under 5 seconds.

---

## Tool & Data Inventory
### Knowledge Sources
- Google Sheets with daily order logs (multiple sheets)
- Internal databases (SQLite)
- Reference documents: PDFs with product and vendor details

### Action Tools
- Python scripts for data ingestion and transformation
- SQL queries for live database access
- APIs for payment gateways and notifications (e.g., email or Slack alerts)

---

## Architecture
The high-level system architecture uses **LangGraph** to orchestrate:

1. **Perception:** Pull data from Google Sheets, PDFs, and databases.
2. **Reasoning:** Apply logic to plan multi-step actions, such as filtering completed/canceled/refunded orders.
3. **Execution:** Trigger Python scripts for automated reporting, alerts, and updates.

![Architecture Diagram](Architecture_Diagram.png)

---

## Repository Structure
