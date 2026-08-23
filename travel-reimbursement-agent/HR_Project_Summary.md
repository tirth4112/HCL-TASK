# Travel Reimbursement AI Agent
**A simplified guide to what I built and how it works**

## 1. What does this project do?
I built an "AI Assistant" that completely automates the process of reviewing employee travel expenses. 

Normally, when an employee submits an expense (like "I spent $500 on a hotel in New York"), a human in HR has to read it, look up the company policy, check if the amount is allowed, and verify the receipts. 

My project does all of this automatically in seconds! It reads the text, understands it, checks the company rules, and decides whether to Approve, Reject, or flag the claim for Manual Review.

---

## 2. How did I build it? (The Tech Stack)

I used some of the newest AI and Database technologies to make this work:

- **PostgreSQL & pgvector:** Instead of just storing normal text, I used an advanced database feature called `pgvector`. This allows the database to "understand" the meaning of words. When an employee submits a hotel claim, `pgvector` instantly searches the database and pulls out the exact hotel policies based on the context, not just simple keyword matches!
- **Large Language Models (Groq AI):** I integrated an ultra-fast AI model to act as the "brain." It reads the messy, natural language sentences from employees and converts them into clean, organized data that computers can understand.
- **LangGraph:** This is a tool I used to keep the AI under control. Instead of letting the AI guess the answers, LangGraph forces the AI to follow a strict, step-by-step checklist—just like a real auditor would.
- **Python Deterministic Engine:** I wrote custom Python code to handle the actual math (like checking if $500 is over the $200 limit). AI is notoriously bad at math, so my system uses AI for reading, but strict Python code for the final financial calculations.

---

## 3. The User Experience
I didn't just write background code; I built an interactive dashboard! 

Using **Jupyter Notebooks**, I created a live interface where you can type in a claim (e.g., "I spent $60 on dinner"). The moment you hit process, the dashboard automatically updates with:
- The final decision (Approved/Rejected)
- Live Pie Charts showing the approval statistics
- An Audit Trail showing exactly which rules the AI checked and when.

---

## 4. Why is this valuable to the company?
1. **Saves Massive Time:** Turns a manual review process that takes days into an automated process that takes 2 seconds.
2. **Zero Math Errors:** The strict Python rules ensure no one is ever reimbursed a penny over the policy limit.
3. **Easy to Update:** Because of `pgvector`, HR can just upload new policy documents to the database, and the AI will automatically learn the new rules without anyone needing to rewrite the code!
