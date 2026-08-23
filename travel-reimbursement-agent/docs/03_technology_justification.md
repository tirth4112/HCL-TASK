# Technology Justification

Why did we choose this specific stack? This document provides a simple, easy-to-read justification for each piece of technology in the assignment.

### 1. Groq (LLM Provider)
**Why we chose it:**
- Blistering fast inference speeds.
- Excellent for agentic reasoning workflows where speed prevents bottlenecks.
- Simple, OpenAI-compatible API structure making it easy to integrate.

**Why not OpenAI/Anthropic:** The assignment specifically requested Groq. However, the `GroqLLMProvider` is written as an abstraction class, meaning we could easily swap it to OpenAI with zero architecture changes.

### 2. PostgreSQL
**Why we chose it:**
- Robust, production-grade relational database.
- It seamlessly holds structured data (Claims, Audit Logs) in the exact same location as vector data, reducing operational complexity.

**Why not MongoDB/Redis:** Redis is volatile (in-memory) and MongoDB is NoSQL. For financial reimbursement data with strict schema requirements (like Audit Logs and Claims), a relational SQL database is the industry standard.

### 3. pgvector (Vector Database)
**Why we chose it:**
- Allows us to do Retrieval-Augmented Generation (RAG) directly inside PostgreSQL.
- We don't have to spin up and pay for a separate vector database (like Pinecone) just to search a small set of policy rules.

**Why not Pinecone/Chroma/FAISS:** The assignment explicitly forbade Pinecone/Chroma/FAISS. `pgvector` keeps the architecture lightweight and contained in a single database.

### 4. LangGraph (Orchestration)
**Why we chose it:**
- Allows us to define the AI Agent as a "State Graph" with clear, deterministic steps.
- Unlike LangChain's basic agents which can enter infinite loops, LangGraph provides absolute control over the flow (e.g., Run Checkers -> Math Engine -> LLM Reasoning).

**Why not AutoGen/CrewAI:** LangGraph is highly suited for cyclic, state-based single-agent workflows and integrates perfectly with our custom python tools.

### 5. Python Deterministic Engine
**Why we chose it:**
- LLMs are terrible at arithmetic and strictly enforcing layered rules. 
- A Python engine calculates the money, and the LLM just explains the Python engine's decision. This guarantees financial accuracy.

### 6. local sentence-transformers (Embeddings)
**Why we chose it:**
- We use `all-MiniLM-L6-v2` to convert text to vectors.
- It is free, runs locally, and requires no API key.
- Perfect for a small corpus of rules (like travel policies).
