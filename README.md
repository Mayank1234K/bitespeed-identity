#  Bitespeed Backend Task – Identity Reconciliation

## Live Application

Base URL:
https://bitespeed-identity-9qa7.onrender.com

API Documentation (Swagger):
https://bitespeed-identity-9qa7.onrender.com/docs


---

#  Problem Overview

FluxKart collects customer contact details (email and phone number) during checkout.

However, a single customer may:
- Use different emails
- Use different phone numbers
- Revisit with partially matching information

The system must intelligently:
- Identify whether incoming contact data belongs to an existing customer
- Link related contacts together
- Maintain a single primary contact
- Convert others into secondary contacts
- Return consolidated identity information

This service solves the identity reconciliation problem.


---

#  Tech Stack

- Python 3.10+
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Render (Cloud Deployment)


---

#  Database Design

Table: contacts

Fields:

- id (Primary Key)
- email (Nullable)
- phoneNumber (Nullable)
- linkedId (Nullable – references primary contact)
- linkPrecedence ("primary" | "secondary")
- createdAt (Auto-generated timestamp)
- updatedAt (Auto-updated timestamp)
- deletedAt (Nullable)


### Data Rules

1. The oldest contact is always the primary contact.
2. All related contacts must link to the primary using linkedId.
3. Secondary contacts reference the primary contact.


---

#  Identity Reconciliation Algorithm

### Step 1: Search Existing Contacts

Find all contacts where:

- email matches OR
- phoneNumber matches


### Step 2: No Existing Contact Found

Create a new contact:
- linkPrecedence = "primary"
- linkedId = null


### Step 3: If Matching Contacts Exist

1. Collect all related contacts.
2. Identify the oldest contact → mark as primary.
3. Convert other primaries into secondary.
4. If new information is introduced:
   - Create a new secondary contact.
5. Return consolidated response.


---

#  API Contract

## Endpoint

POST /identify


## Request Body

At least one of the fields must be provided.

{
  "email": "string?",
  "phoneNumber": "string?"
}


---

## Successful Response (200)

{
  "contact": {
    "primaryContatctId": 1,
    "emails": [
      "lorraine@hillvalley.edu",
      "mcfly@hillvalley.edu"
    ],
    "phoneNumbers": [
      "123456"
    ],
    "secondaryContactIds": [
      2
    ]
  }
}


---

#  Example Scenarios

### Scenario 1: New Customer

Input:
{
  "email": "new@user.com",
  "phoneNumber": "999999"
}

Output:
- New primary contact created.


### Scenario 2: Existing Customer with Same Phone

Input:
{
  "email": "another@email.com",
  "phoneNumber": "123456"
}

Output:
- Secondary contact created.
- Linked to existing primary.


### Scenario 3: Two Separate Primaries Get Linked

If two primary contacts share a common field in a new request:
- The oldest remains primary.
- The newer one becomes secondary.
- Data is merged.


---

# Edge Cases Handled

✔ New contact creation  
✔ Multiple secondary contacts  
✔ Primary-to-secondary conversion  
✔ Deduplication of emails  
✔ Deduplication of phone numbers  
✔ Linking two independent primary records  
✔ Handling null values safely  


---

# Project Structure

bitespeed-identity/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│
├── requirements.txt
├── .env (not committed)
├── .gitignore
└── README.md


---

#  Running Locally

1. Clone repository

git clone https://github.com/Mayank1234K/bitespeed-identity
cd bitespeed-identity


2. Create virtual environment

python -m venv venv
source venv/bin/activate  (Windows: venv\Scripts\activate)


3. Install dependencies

pip install -r requirements.txt


4. Create .env file

DATABASE_URL=your_postgres_connection_string


5. Start server

uvicorn app.main:app --reload


Open:
http://127.0.0.1:8000/docs


---

#  Deployment

The application is deployed on Render.

Environment Variable Required:
DATABASE_URL

Start Command:
uvicorn app.main:app --host 0.0.0.0 --port $PORT


---

#  Design Decisions

- Oldest contact remains authoritative primary.
- All merging is done at application layer.
- Database consistency maintained via ORM.
- Separation of concerns:
  - Database Layer
  - Service Layer
  - API Layer
- Stateless API design.


---

#  Future Improvements

- Add soft delete logic support
- Add unit tests
- Add indexing optimizations
- Add transaction-level locking for high concurrency
- Add caching layer for performance


---

# Author

Mayank K  
Backend Developer | Python | FastAPI | System Design