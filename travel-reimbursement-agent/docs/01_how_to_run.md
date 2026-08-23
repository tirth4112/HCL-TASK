# How to Run the Project

This guide explains how to get the Travel Reimbursement Agent running locally on your machine.

### 1. Resolve Network/Pip Issues (If Any)
Ensure you are connected to the internet and can reach Python's package index.
Run the following command in your terminal from the project folder (`travel-reimbursement-agent`):
```bash
python -m pip install -r requirements.txt
```
*(Note: If `pip install` fails due to DNS issues, wait for your network connection to stabilize and try again.)*

### 2. Configure Environment Variables
1. A `.env` file has already been generated for you with your provided Render PostgreSQL credentials and Groq API key.
2. Ensure the `.env` file looks like this:
```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama3-70b-8192
DATABASE_URL=postgresql+psycopg://hcl_db_4p89_user:your_pass_here@dpg-...-a.oregon-postgres.render.com/hcl_db_4p89
```

### 3. Run the Jupyter Notebook
The assignment requires the main submission to be an executable Jupyter Notebook.
1. Open VS Code or Jupyter Lab.
2. Open the file `yourname.ipynb`.
3. In VS Code, click **"Run All"** at the top of the notebook.
4. The notebook will automatically:
   - Connect to PostgreSQL and create schemas.
   - Ingest `data/policy.json` into `pgvector`.
   - Process the 5 claims from `data/claims.json`.
   - Generate the final output JSON.
   - Plot the Plotly dashboard.

### 4. (Optional) Testing via Python Script
If you prefer running without Jupyter, you can easily convert and run the notebook as a script:
```bash
jupyter nbconvert --to script yourname.ipynb
python yourname.py
```
