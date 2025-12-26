# Persona-Based Conversational Assessment System

## Project Overview
This project aims to build a **persona-based conversational assessment platform** that evaluates candidates through adaptive, interview-style conversations instead of static MCQs. The system leverages **prompt engineering** as the core intelligence layer, ensuring human-like interaction, reduced cheating, and holistic evaluation.

The interviewer’s **behavior, memory, adaptability, and judgment** are fully controlled through structured prompts rather than hard-coded logic.

---

## Objectives
- Replace traditional MCQ-based assessments with conversational evaluation
- Dynamically adapt questions based on user responses
- Assess reasoning, communication, and adaptability
- Provide fair, personalized, and anti-cheating assessments
- Maintain explainable and modular system design

---

## Core Assessment Dimensions
Every question and evaluation must map to at least one of the following:
- Logical Thinking
- Communication Skills
- Adaptability

---

## High-Level Architecture

User
↓
Chat UI
↓
Conversation Controller (State Machine)
↓
Persona Engine
↓
Prompt-Based Question Generator (Gemini)
↓
Response Analyzer
↓
Scoring Engine
↓
Adaptive Decision Maker
↓
Result Generator

---

## Prompt-Driven Design

### 1. Interviewer Persona Prompt
Defines:
- Interviewer identity and tone
- Behavioral rules (one question at a time, no MCQs)
- Assessment philosophy (reasoning over recall)
- Anti-cheating and follow-up logic

This prompt ensures the AI behaves like a real interviewer.

---

### 2. Candidate Context Injection
Injected before every question:
- Candidate background
- Persona tag
- Previous response summaries
- Observed strengths or weaknesses

This acts as the system’s **memory layer**.

---

### 3. Question Generation Prompt
Inputs:
- Persona
- Difficulty level
- Topic focus
- Last answer summary

Output:
- One open-ended, assignment-style question

Rules:
- No definitions or factual recall
- No multiple questions in one turn
- Must assess at least one core dimension

---

### 4. Response Evaluation Prompt
A separate evaluator prompt that:
- Reviews the candidate’s answer
- Outputs structured scores and insights (JSON)
- Does NOT interact with the candidate

Evaluates:
- Depth of reasoning
- Clarity
- Adaptability
- Authenticity

---

### 5. Adaptive Decision Prompt
Uses evaluation output to:
- Increase or reduce difficulty
- Change question framing
- Add or remove constraints

Ensures no two interviews follow the same path.

---

### 6. Result Generation Prompt
At interview completion, generates:
- Skill-level summary
- Strengths
- Improvement areas
- Overall assessment narrative

Tone: neutral, professional, growth-oriented.

---

## Technology Stack

### Backend
- **Language:** Python 3.12
- **Framework:** Flask
- **Session Management:** Flask-Session
- **Cache/State Store:** Redis

### AI & NLP
- **LLM Provider:** Google Gemini (Gemini 1.5 Flash)
- **API Access:** Gemini API Key (via environment variables)
- **Prompt Control:** Structured prompt templates
- **NLP Tools:** SpaCy, NLTK

### Frontend (Later Phase)
- Next.js (React + TypeScript)
- Tailwind CSS
- Chat-style UI

### Reporting
- ReportLab (PDF generation)
- Matplotlib (Score visualization)

---

## Security & Configuration
- Gemini API Key stored in `.env`
- No hard-coded credentials
- Session-based interview isolation

---

## Implementation Strategy (Permission-Based)

⚠️ **Important Rule**  
Before starting **any implementation phase**, explicit permission will be taken.

No coding, setup, or execution will begin unless approval is given for that phase.

---

## Planned Implementation Phases (Approval Required)

### Phase 1 – Basic Conversation Skeleton
- Basic Chat UI (input + response)
- Conversation Controller (start / ask / receive / end)

⏸ *Awaiting permission before starting Phase 1*

---

### Phase 2 – Rule-Based Persona Engine
- Initial profiling questions
- Rule-based persona tagging

⏸ *Requires explicit approval*

---

### Phase 3 – Gemini-Powered Question Generation
- Gemini API integration
- Prompt-based interviewer logic

⏸ *Requires explicit approval*

---

### Phase 4 – Response Analysis & Scoring
- Basic NLP analysis
- Structured scoring output

⏸ *Requires explicit approval*

---

### Phase 5 – Adaptive Logic
- Difficulty adjustment
- Scenario shifting

⏸ *Requires explicit approval*

---

### Phase 6 – Result Generation & PDF Report
- Final assessment summary
- Visual score report

⏸ *Requires explicit approval*

---

## Key Design Principle
> Prompt engineering is the **core logic layer**, not an add-on.

This ensures modularity, explainability, and future model replacement without redesigning the system.

---

## Status
📌 **Specification completed**  
⏸ **Implementation not started (waiting for permission)**

