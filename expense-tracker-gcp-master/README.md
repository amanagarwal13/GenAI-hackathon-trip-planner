# Expense Tracker Agent

## Description

This project is an AI-powered expense tracking application. It uses a conversational agent (ExpenseBot) to help users manage their expenses and budgets. Users can interact with the agent to add, update, delete, and view expenses, set and manage budgets, and get summaries of their spending.

## Features

- **Expense Management:** Add, update, delete, and view expenses.
- **Budgeting:** Set, update, delete, and view monthly budgets.
- **Expense Summaries:** Get a summary of total spending and spending by category for the current month.
- **Expense History:** Retrieve expenses by date, date range, or category.
- **Category Management:** List all expense categories.
- **Natural Language Interaction:** Interact with the ExpenseBot using natural language.
- **Automatic Categorization (with confirmation):** The agent can suggest expense categories based on the expense name.
- **Currency:** Supports Indian Rupees (INR).

## Technologies Used

- Python
- Google ADK (Agent Development Kit)
- Pydantic (for data validation)
- Google Cloud Firestore (as the database)
- Gemini AI Model

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd cv-expense-tracker
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv env
    .\env\Scripts\Activate.ps1 
    ```
    (For Windows PowerShell)
    ```bash
    source env/bin/activate
    ```
    (For Linux/macOS)


3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Google Cloud Firestore:**
    *   Create a Firebase project and enable Firestore.
    *   Download your service account key JSON file and save it as `service-acc.json` in the root directory of the project.
    *   Ensure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set to point to this file, or the application is configured to use it directly (as seen in `main.py` if applicable).

## Usage

To run the agent, execute the `main.py` script:

```bash
python main.py
```

This will typically start a local server or interface where you can interact with the ExpenseBot.

## Agent Capabilities (Tools)

The ExpenseBot utilizes the following functions to manage financial data:

*   `add_expense`: Adds a new expense.
*   `get_all_expenses`: Retrieves all recorded expenses.
*   `get_expense_by_date`: Fetches expenses for a specific date.
*   `get_expense_by_date_range`: Retrieves expenses within a given date range.
*   `update_expense`: Modifies an existing expense.
*   `delete_expense`: Removes an expense.
*   `get_expenses_by_category`: Lists expenses belonging to a particular category.
*   `get_all_categories`: Shows all unique expense categories.
*   `add_budget`: Sets a budget for a specific month and year.
*   `get_current_month_budget`: Retrieves the budget for the current month.
*   `update_budget`: Modifies an existing budget.
*   `delete_budget`: Removes a budget.
*   `get_expense_summary`: Provides a summary of expenses for the current month, including total spending, category breakdown, and budget comparison.

Interact with the agent by providing commands related to these capabilities in natural language. For example: "Add an expense of 500 rupees for groceries today," or "What's my budget for this month?".
