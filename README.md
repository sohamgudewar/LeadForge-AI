# LeadForge AI

LeadForge AI is a multi-agent AI SDR (Sales Development Representative) platform that automates lead research, qualification, personalization, and outreach generation.

The system uses a LangGraph-based agent workflow to analyze a company, enrich lead information, score lead quality, generate personalized outreach emails, and review the generated content before delivery.

---

## Features

### Knowledge Agent
Provides internal company knowledge and business context.

### Research Agent
Analyzes a target company and identifies:

- Industry
- Business challenges
- Growth opportunities
- Market positioning

### Lead Enrichment Agent
Generates lead intelligence including:

- Company size
- Target buyers
- Decision makers
- Relevant departments
- Outreach priority

### Lead Scoring Agent
Qualifies leads and assigns a lead score based on:

- Market opportunity
- Business needs
- Growth potential
- Expected budget

### Personalization Agent
Creates a personalized outreach angle using:

- Company research
- Internal knowledge
- Lead enrichment data

### Email Agent
Generates a cold outreach email with:

- Subject line
- Personalized messaging
- Call-to-action

### Reviewer Agent
Reviews the generated outreach package and evaluates:

- Research quality
- Personalization quality
- Email quality
- Overall SDR readiness

### Lead Management API
Stores generated leads and outreach data in PostgreSQL.

---

# Agent Workflow

```text
Knowledge Agent
      ↓
Research Agent
      ↓
Enrichment Agent
      ↓
Lead Scoring Agent
      ↓
Personalization Agent
      ↓
Email Agent
      ↓
Reviewer Agent
```

---

## Tech Stack

### LangGraph

Used for building the multi-agent workflow.

Why?

- State-based agent orchestration
- Agent chaining
- Workflow management
- Scalable architecture for future agents

---

### Google Gemini 2.5 Flash

Used as the LLM powering all agents.

Why?

- Fast inference
- Strong reasoning capability
- Cost efficient
- Suitable for agentic workflows

---

### FastAPI

Used for backend APIs.

Why?

- High performance
- Easy API development
- Automatic OpenAPI documentation
- Production-ready framework

---

### PostgreSQL

Used for lead storage.

Why?

- Reliable relational database
- Structured lead management
- Easy querying and reporting
- Industry standard

---

### SQLAlchemy

Used as ORM.

Why?

- Database abstraction
- Cleaner database operations
- Easier maintenance

---

### React

Used for frontend development.

Why?

- Component-based architecture
- Fast UI development
- Easy API integration

---

### Tailwind CSS

Used for styling.

Why?

- Rapid UI development
- Utility-first approach
- Consistent design system

---

## API Endpoints

### Generate Outreach

POST

```http
/run-agent
```

Request:

```json
{
  "company": "Slack"
}
```

---

### Get All Leads

GET

```http
/leads
```

---

### Get Lead By ID

GET

```http
/lead/{lead_id}
```

---

## Project Structure

```text
backend/
│
├── agents/
│   ├── knowledge_agent.py
│   ├── research_agent.py
│   ├── enrichment_agent.py
│   ├── lead_scoring_agent.py
│   ├── personalization_agent.py
│   ├── email_agent.py
│   └── reviewer_agent.py
│
├── api/
├── database/
├── graph/
├── models/
│
└── main.py

frontend/
│
├── src/
├── public/
│
└── App.jsx
```

---

## Future Improvements

- Retrieval-Augmented Generation (RAG)
- Document Upload Knowledge Base
- Vector Database Integration
- Apollo / Clearbit Lead Enrichment
- Reviewer Feedback Loop
- Deployment on Railway and Vercel
- Docker container
---

## Author

Soham Gudewar

GitHub:
https://github.com/sohamgudewar