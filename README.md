# Secure Enterprise Chatbot System

Welcome to the **Secure Enterprise Chatbot System**, an advanced solution tailored for businesses that prioritize data privacy while leveraging AI chatbot capabilities. This system integrates OpenAI's LLM, Vectara's RAG capabilities, and a privacy-focused LLM for censoring sensitive information. With direct connectivity to enterprise databases and a web interface built with Next.js, it ensures secure, efficient, and personalized customer interactions.

## Key Features

- **Next.js Web Interface:** A modern, responsive UI for interacting with the chatbot.
- **Python Backend:** Robust and scalable Python services for chatbot logic and data handling.
- **PostgreSQL Database:** Secure storage for chat history and sensitive data with predefined schemas.
- **Supabase Integration:** Enhanced database functionalities with Supabase's real-time capabilities.

## Prerequisites

Before you begin, ensure you have the following installed:

- Node.js and npm (for Next.js)
- Python 3.8 or later
- PostgreSQL
- A Supabase account (for database and real-time functionalities)

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/yourgithubusername/projectname.git
cd projectname
```

## Set Up the PostgreSQL Database
1. Install PostgreSQL and start the PostgreSQL service.
2. Create a database for the project:

```sql
CREATE DATABASE chatbotdb;
```

3. Use the following schema to set up the chat history table:
```sql
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    username VARCHAR(50),
    message TEXT NOT NULL,
    response TEXT NOT NULL
);

```
## Configure Supabase
1. Sign up or log in to your Supabase account.
2. Create a new project and note your project's API keys and connection strings.
3. Integrate Supabase with your application by following the Supabase Documentation.

## Set Up the Next.js Frontend
Navigate to the frontend directory and install the dependencies:

```bash
cd frontend
npm install
```

Run the development server:
```bash
npm run dev
```

Visit http://localhost:3000 in your browser to see the application.

## Install Python Dependencies
Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Running the Application
Navigate back to the root directory and start the backend server:

```bash
python src/main.py
```
