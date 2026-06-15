SmartReach AI CRM

SmartReach AI CRM is a full-stack AI-powered Customer Relationship Management (CRM) platform built as part of the Xeno Engineering Internship Assignment.

FEATURES: 
Customer Management, 
View customer database, 
Add new customers, 
Customer activity tracking, 
Search customers,
Audience Segmentation,
Create dynamic customer segments,
Define targeting rules,
Manage campaign audiences,
Campaign Management,
Create marketing campaigns,
Track campaign performance,
Campaign listing and details,
AI Campaign Generator,
Generate campaign plans using AI,
Natural language campaign creation,
AI-powered marketing suggestions,
Fallback responses when AI API is unavailable,
Analytics Dashboard,
Customer insights,
Campaign metrics,
Delivery statistics,
Performance monitoring,
TECH STACK:
Frontend,
React.js,
Vite,
Tailwind CSS,
Axios,
Backend,
FastAPI,
SQLAlchemy,
SQLite,
Pydantic,
AI Integration,
Google Gemini API,
Project Structure,
xeno-ai-crm/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── smartreach.db
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
└── channel_service/
Installation
Backend
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload

Backend runs on:

http://localhost:8000
Frontend
cd frontend

npm install

npm run dev

Frontend runs on:

http://localhost:5173
API Endpoints
Customers
GET /api/customers
POST /api/customers
Segments
GET /api/segments
POST /api/segments
Campaigns
GET /api/campaigns
POST /api/campaigns
AI
POST /api/ai/generate-campaign
POST /api/ai/analyze-insights
Screenshots :
Dashboard,
Customers,
Segments,
Campaigns,
AI Generator,
Analytics,
Assignment Highlights:
Full-stack CRM application,
Customer management system,
Audience segmentation engine,
Campaign management module,
AI-powered campaign generation,
FastAPI backend,
React frontend,
SQLite database integration,
Author:

Simran Lakhotia
