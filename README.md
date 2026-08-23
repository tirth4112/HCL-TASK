# Travel Reimbursement Approval Agent

## Project Overview
An intelligent, agentic AI system designed to process travel reimbursement claims. It evaluates claims against company policy, calculates approved and deducted amounts deterministically, uses Groq for reasoning, and stores results and embeddings in PostgreSQL using `pgvector`.

## Features
- End-to-end LangGraph agent workflow.
- RAG using PostgreSQL `pgvector` for policy retrieval.
- Strict deterministic engine for financial math (no LLM hallucination).
- Groq LLM integration for reasoning and explanation.
- Dashboard generation with Plotly.
- Built-in audit trail logged to PostgreSQL.

## Architecture
1. **Validation**: Validate claim data.
2. **Retrieval**: Retrieve relevant policy rules using `pgvector`.
3. **Tools**: Execute deterministic tools (Limits, Receipts, Airfare, Timeliness, Approval).
4. **Engine**: Apply precedence rules to output financial calculations.
5. **Reasoning**: Groq explains the decision based on exact context.
6. **Output**: Validates schema and returns structured JSON.

## Tech Stack
- Python 3.10+
- Groq
- LangGraph
- PostgreSQL + pgvector
- SQLAlchemy
- Sentence-Transformers
- Pydantic
- Plotly
- Jupyter Notebook

## Prerequisites
- PostgreSQL instance
- Python 3.10+

## PostgreSQL Setup
1. Create your database: `CREATE DATABASE travel_reimbursement;`
2. Connect to it and enable pgvector: `CREATE EXTENSION IF NOT EXISTS vector;`

## Groq Setup
Get an API key from Groq and add it to your `.env` file.

## Environment Variables
Create a `.env` file from `.env.example`:
```
GROQ_API_KEY=your_key
GROQ_MODEL=llama3-70b-8192
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/travel_reimbursement
```

## Installation
```bash
pip install -r requirements.txt
```

## Running Notebook
Open `yourname.ipynb` in Jupyter and run all cells from top to bottom.

## Expected Results
- **CLM-001**: APPROVE ($1110)
- **CLM-002**: REJECT ($0)
- **CLM-003**: PARTIAL_APPROVE ($840)
- **CLM-004**: MANUAL_REVIEW
- **CLM-005**: MANUAL_REVIEW

## Project Structure
- `data/`: Claims and policies JSON
- `src/`: Core logic and LangGraph modules
- `yourname.ipynb`: Main notebook demonstrating the flow

## Design Decisions
- **Deterministic Engine**: Mathematical decisions are hardcoded in Python to prevent LLM hallucinations.
- **pgvector**: Keeps embeddings and relational data (audit logs) in one system.

## Limitations
- Small policy corpus
- Local Sentence-Transformers instead of paid embeddings to keep it lightweight
- No real OCR

## Future Improvements
- OCR receipt extraction
- Fraud detection
- Full human approval portal

## Interview Demo
See the "Interview Explanation" section in the notebook for a concise pitch.
