# Travel Reimbursement Approval Agent

## 📌 Project Overview
This project is an autonomous, AI-driven Travel Reimbursement Agent designed to evaluate employee expense claims. It seamlessly parses natural language inputs or structured JSON data, maps the claims against strict corporate travel policies using LangGraph and semantic search, and enforces deterministic financial rules to reach a final decision (Approve, Partially Approve, Reject, or Route for Manual Review).

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9+
- Jupyter Lab or Jupyter Notebook

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/tirth4112/HCL-TASK.git
   cd HCL-TASK
   ```
2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the example environment file and add your Groq API key:
   ```bash
   cp .env.example .env
   ```

### Environment Variables
Configure your `.env` file with the following:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-70b-8192
DATABASE_URL=sqlite:///local_db.sqlite3
```
*Note: The system features a built-in Mock Mode. If `GROQ_API_KEY` is empty or omitted, it will safely fall back to generating deterministic mock JSON, allowing the notebook to run seamlessly without requiring paid API credits.*

## 💻 How to Run the Demo

1. Start Jupyter Lab:
   ```bash
   jupyter lab
   ```
2. Open `TirthPanchal.ipynb`.
3. In the top menu, click **Kernel** -> **Restart Kernel and Run All Cells...**
4. **Interactive Dashboard:** Scroll down to the interactive UI. You can type natural language claims (e.g., *"I spent $100 on meals"*) and click **Process Manual Input**. The Live Dashboard, Plotly charts, Audit Trail, and Final JSON outputs will all update dynamically in real-time.

## 🧠 Key Design Choices & Architecture

- **LangGraph Workflow:** The approval process is modeled as a directed state graph. This prevents the LLM from wandering off-topic and forces it to follow a strict, repeatable auditing checklist.
- **Deterministic Math Engine:** AI models are prone to hallucinating math. I designed the system so the LLM is only used for *reading and parsing* unstructured text. All actual financial checks (e.g., verifying limits, per-diems, and receipt thresholds) are handled by a strict, deterministic Python rule engine.
- **Local Vector Database:** The system uses a local SQLite database for semantic policy search (RAG) rather than relying on an external cloud database. This guarantees zero-latency lookups and complete reliability during demonstrations.

## 📊 Sample Outputs

When providing the claim: *"I spent $2400 on a Business-class international flight"*, the agent outputs:
```json
{
  "claim_id": "CLM-004",
  "decision": "MANUAL_REVIEW",
  "approved_amount": 0.0,
  "deducted_amount": 0.0,
  "missing_docs": [],
  "policy_refs": ["POL-AIR-01", "POL-APR-03"],
  "confidence": 0.95,
  "explanation": "Routed to manual review because business-class airfare requires exception handling (POL-AIR-01) and the total exceeds the auto-approval threshold (POL-APR-03)."
}
```

## ⚠️ Assumptions and Limitations
- **Currency:** Assumes all transactions and policy limits are in USD. No currency conversion logic is implemented.
- **Receipt Parsing:** The current UI assumes the user provides a boolean flag for `receipt_attached`. In a production system, this would be hooked up to an OCR tool (like AWS Textract or Azure Document Intelligence) to parse physical image files.
- **Single User Context:** The interactive Jupyter dashboard manages global state for the session. In a production API, state would be managed per-request via a robust caching layer like Redis.

## 🎥 Demo & UI Screenshots
I have built a complete, interactive Plotly dashboard UI directly within Jupyter Notebook. 
A screenshot of the user interface processing a claim can be found in the root of this repository:
- **`UI SS_1.png`** (Live Dashboard & Audit Trail)

*(Note: A comprehensive video walkthrough of the Jupyter Lab interface handling live claims is available upon request).*
