# Copyright 2022 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     https://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent # type: ignore
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from google.cloud.firestore import AsyncClient, FieldFilter, DocumentReference  # type: ignore


firestore_client: AsyncClient = AsyncClient()


def date_system_prompt() -> str:
    return (
        "Today's date is "
        + str(datetime.now().date())
        + ". Please use this date for all finding relative other dates. Example: finding yesterday, tomorrow, weekend."
    )


EXPENSE_COLLECTION_NAME = "expenses"
BUDGET_COLLECTION_NAME = "budgets"


class ExpenseModel(BaseModel):
    name: str
    amount: float
    date: str
    category: str


class ExpenseSchema(ExpenseModel):
    id: str = Field(description="ID of the expense")
    date: datetime = Field(description="Date of the expense")  # type: ignore


class AddExpenseInputSchema(BaseModel):
    name: str = Field(description="Name of the expense")
    amount: float = Field(description="Amount of the expense")
    date: str = Field(description="Date of the expense, format: YYYY-MM-DD")
    category: str = Field(description="Category of the expense")


class GetAllExpensesOutputSchema(BaseModel):
    expenses: list[ExpenseSchema] = Field(description="List of all expenses")
    total: float = Field(description="Total amount of all expenses")


class UpdateExpenseInputSchema(BaseModel):
    name: Optional[str] = Field(
        None,
        description="New name of the expense, if not provided, old name will be used",
    )
    date: Optional[str] = Field(
        None,
        description="New date of the expense, if not provided, old date will be used, format: YYYY-MM-DD",
    )
    amount: Optional[float] = Field(
        None,
        description="New amount of the expense, if not provided, old amount will be used",
    )
    category: Optional[str] = Field(
        None,
        description="New category of the expense, if not provided, old category will be used",
    )


class ExpenseSummaryOutputSchema(BaseModel):
    total: float = Field(description="Total amount of all expenses")
    categories: dict[str, float] = Field(
        description="Total amount of expenses by category"
    )
    expenses: list[ExpenseSchema] = Field(
        description="List of all expenses for current month"
    )
    budget: Optional[str]


async def add_expense(name: str, amount: str, date: str, category: str) -> str:
    """Adds a new expense to the Firestore database.

    Args:
        name (str): The name of the expense.
        amount (str): The amount of the expense.
        date (str): The date of the expense in YYYY-MM-DD format.
        category (str): The category of the expense.

    Returns:
        str: A message indicating the expense was added successfully, along with the document ID.
    """
    data = AddExpenseInputSchema(
        name=name,
        amount=float(amount),
        date=date,
        category=category,
    )
    expense = ExpenseModel(
        name=data.name,
        amount=data.amount,
        date=datetime.strptime(data.date, "%Y-%m-%d").isoformat(),
        category=data.category,
    )
    expense_dict = expense.model_dump()
    collection_ref = firestore_client.collection(EXPENSE_COLLECTION_NAME)
    doc_ref: DocumentReference = (await collection_ref.add(expense_dict))[1]
    return "Expense added successfully with ID: " + doc_ref.id


async def get_all_expenses() -> str:
    """
    Asynchronously retrieves all expenses from the Firestore database, calculates the total amount,
    and returns the data as a JSON string.
    Returns:
        str: A JSON string representing all expenses and their total amount, formatted according
             to the GetAllExpensesOutputSchema.
    """
    collection_ref = firestore_client.collection(EXPENSE_COLLECTION_NAME)
    docs = await collection_ref.get()

    expenses = [
        ExpenseSchema(
            id=doc.id,
            **doc.to_dict(),
        )
        for doc in docs
    ]
    total = sum(expense.amount for expense in expenses)
    return GetAllExpensesOutputSchema(expenses=expenses, total=total).model_dump_json()


async def get_expense_by_date(date: str) -> str:
    """
    Retrieve expenses for a specific date and return them along with the total amount.
    Args:
        date (str): Date of the expense in the format 'YYYY-MM-DD'.
    Returns:
        str: A JSON string containing a list of expenses for the given date and the total amount.
    Raises:
        ValueError: If the provided date string does not match the expected format.
        Exception: If there is an error retrieving expenses from the database.
    """

    collection_ref = firestore_client.collection(EXPENSE_COLLECTION_NAME)
    docs = await collection_ref.where(
        filter=FieldFilter(
            "date", "==", datetime.strptime(date, "%Y-%m-%d").isoformat()
        )
    ).get()
    expenses = [
        ExpenseSchema(
            id=doc.id,
            **doc.to_dict(),
        )
        for doc in docs
    ]
    total = sum(expense.amount for expense in expenses)
    return GetAllExpensesOutputSchema(expenses=expenses, total=total).model_dump_json()


async def get_expense_by_date_range(start_date: str, end_date: str) -> str:
    """
    Retrieve expenses within a specified date range.
    Args:
        start_date (str): The start date of the range in "YYYY-MM-DD" format.
        end_date (str): The end date of the range in "YYYY-MM-DD" format.
    Returns:
        str: A JSON string representing the expenses and their total amount within the specified date range.
    Raises:
        ValueError: If the date format is incorrect.
        Exception: For any errors during Firestore operations.
    """

    collection_ref = firestore_client.collection(EXPENSE_COLLECTION_NAME)
    docs = (
        await collection_ref.where(
            filter=FieldFilter(
                "date", ">=", datetime.strptime(start_date, "%Y-%m-%d").isoformat()
            )
        )
        .where(
            filter=FieldFilter(
                "date", "<=", datetime.strptime(end_date, "%Y-%m-%d").isoformat()
            )
        )
        .get()
    )

    expenses = [
        ExpenseSchema(
            id=doc.id,
            **doc.to_dict(),
        )
        for doc in docs
    ]
    total = sum(expense.amount for expense in expenses)
    return GetAllExpensesOutputSchema(expenses=expenses, total=total).model_dump_json()


async def update_expense(
    expense_id: str,
    name: Optional[str],
    amount: Optional[float],
    date: Optional[str],
    category: Optional[str],
) -> str:
    """
    Asynchronously updates an existing expense in the Firestore database.
    Args:
        expense_id (str): The unique identifier of the expense to update.
        name (Optional[str], optional): New name of the expense. If not provided, the existing name is retained.
        amount (Optional[float], optional): New amount of the expense. If not provided, the existing amount is retained.
        date (Optional[str], optional): New date of the expense in 'YYYY-MM-DD' format. If not provided, the existing date is retained.
        category (Optional[str], optional): New category of the expense. If not provided, the existing category is retained.
    Returns:
        str: A message indicating whether the expense was updated successfully or if the expense was not found.
    """

    collection_ref = firestore_client.collection(EXPENSE_COLLECTION_NAME)
    doc_ref: DocumentReference = collection_ref.document(expense_id)
    doc = await doc_ref.get()
    if not doc.exists:
        return "Expense not found"

    doc_dict = doc.to_dict()
    data = UpdateExpenseInputSchema(
        name=name,
        amount=amount,
        date=date,
        category=category,
    )
    updated_data = data.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        if value is not None:
            doc_dict[key] = (
                datetime.strptime(value, "%Y-%m-%d").isoformat()
                if key == "date"
                else value
            )

    await doc_ref.set(doc_dict, merge=True)
    return "Expense updated successfully"


async def delete_expense(expense_id: str) -> str:
    """
    Asynchronously deletes an expense document from the Firestore collection by its ID.

    Args:
        expense_id (str): The unique identifier of the expense document to delete.

    Returns:
        str: A confirmation message indicating successful deletion.

    Raises:
        google.api_core.exceptions.NotFound: If the document with the given ID does not exist.
        google.api_core.exceptions.GoogleAPICallError: If an error occurs during the deletion process.
    """
    collection_ref = firestore_client.collection(EXPENSE_COLLECTION_NAME)
    doc_ref: DocumentReference = collection_ref.document(expense_id)
    await doc_ref.delete()
    return "Expense deleted successfully"


async def get_expenses_by_category(category: str) -> str:
    """
    Asynchronously retrieves all expenses from the Firestore collection that match the specified category.
    Args:
        category (str): The category of expenses to filter by.
    Returns:
        str: A JSON string representing the list of matching expenses and their total amount, serialized using GetAllExpensesOutputSchema.
    Raises:
        Any exceptions raised by Firestore client operations or schema validation.
    """
    collection_ref = firestore_client.collection(EXPENSE_COLLECTION_NAME)
    docs = await collection_ref.where(
        filter=FieldFilter("category", "==", category)
    ).get()

    expenses = [
        ExpenseSchema(
            id=doc.id,
            **doc.to_dict(),
        )
        for doc in docs
    ]
    total = sum(expense.amount for expense in expenses)
    return GetAllExpensesOutputSchema(expenses=expenses, total=total).model_dump_json()


async def get_all_categories() -> list[str]:
    """
    Asynchronously retrieves all unique expense categories from the Firestore collection.

    Returns:
        list[str]: A list of unique category names found in the expense documents.
    """
    collection_ref = firestore_client.collection(EXPENSE_COLLECTION_NAME)
    docs = await collection_ref.get()
    categories = set()
    for doc in docs:
        data = doc.to_dict()
        if "category" in data:
            categories.add(data["category"])
    return list(categories)


class BudgetModel(BaseModel):
    amount: float = Field(description="Monthly budget amount")
    month: int = Field(description="Month of the budget")
    year: int = Field(description="Year of the budget")


class BudgetSchema(BudgetModel):
    id: str = Field(description="ID of the budget")


class UpdateBudgetInputSchema(BaseModel):
    amount: Optional[float] = Field(
        None,
        description="New budget amount, if not provided, old amount will be used",
    )
    month: Optional[int] = Field(
        None,
        description="New month of the budget, if not provided, old month will be used",
    )
    year: Optional[int] = Field(
        None,
        description="New year of the budget, if not provided, old year will be used",
    )


async def add_budget(amount: str, month: str, year: str) -> str:
    """
    Asynchronously adds a new budget entry to the Firestore database.

    Args:
        amount (str): The budget amount as a string, which will be converted to a float.
        month (str): The month for the budget as a string, which will be converted to an integer.
        year (str): The year for the budget as a string, which will be converted to an integer.

    Returns:
        str: A success message containing the ID of the newly added budget document.

    Raises:
        ValueError: If the amount, month, or year cannot be converted to the appropriate type.
        Exception: If there is an error adding the budget to the Firestore database.
    """
    budget = BudgetModel(
        amount=float(amount),
        month=int(month),
        year=int(year),
    )
    budget_dict = budget.model_dump()
    collection_ref = firestore_client.collection(BUDGET_COLLECTION_NAME)
    doc_ref: DocumentReference = (await collection_ref.add(budget_dict))[1]
    return "Budget added successfully with ID: " + doc_ref.id


async def get_current_month_budget() -> Optional[str]:
    """
    Asynchronously retrieves the budget for the current month and year from the Firestore database.
    Returns:
        Optional[str]: A JSON string representing the current month's budget if found, otherwise None.
    """
    collection_ref = firestore_client.collection(BUDGET_COLLECTION_NAME)
    today = datetime.now()
    docs = (
        await collection_ref.where(filter=FieldFilter("month", "==", today.month))
        .where(filter=FieldFilter("year", "==", today.year))
        .get()
    )

    if not docs:
        return None

    budget = BudgetSchema(
        id=docs[0].id,
        **docs[0].to_dict(),
    )
    return budget.model_dump_json()


async def update_budget(
    budget_id: str, amount: Optional[float], month: Optional[int], year: Optional[int]
) -> str:
    """
    Asynchronously updates an existing budget entry in the Firestore database.

    Args:
        budget_id (str): The unique identifier of the budget to update.
        amount (Optional[float], optional): The new budget amount. If not provided, the existing amount is retained.
        month (Optional[int], optional): The new month for the budget. If not provided, the existing month is retained.
        year (Optional[int], optional): The new year for the budget. If not provided, the existing year is retained.

    Returns:
        str: A message indicating the result of the update operation ("Budget updated successfully" or "Budget not found").
    """

    data = UpdateBudgetInputSchema(
        amount=amount,
        month=month,
        year=year,
    )
    collection_ref = firestore_client.collection(BUDGET_COLLECTION_NAME)
    doc_ref: DocumentReference = collection_ref.document(budget_id)
    doc = await doc_ref.get()
    if not doc.exists:
        return "Budget not found"
    budget = BudgetModel.model_validate(doc.to_dict())
    if data.amount:
        budget.amount = data.amount
    if data.month:
        budget.month = data.month
    if data.year:
        budget.year = data.year
    await doc_ref.set(budget.model_dump(), merge=True)
    return "Budget updated successfully"


async def delete_budget(budget_id: str) -> str:
    """
    Asynchronously deletes a budget document from the Firestore database by its ID.

    Args:
        budget_id (str): The unique identifier of the budget document to delete.

    Returns:
        str: A confirmation message indicating successful deletion.

    Raises:
        google.api_core.exceptions.NotFound: If the document with the given ID does not exist.
        google.api_core.exceptions.GoogleAPICallError: If an error occurs during the deletion process.
    """
    collection_ref = firestore_client.collection(BUDGET_COLLECTION_NAME)
    doc_ref: DocumentReference = collection_ref.document(budget_id)
    await doc_ref.delete()
    return "Budget deleted successfully"


async def get_expense_summary() -> str:
    """
    Asynchronously retrieves a summary of expenses for the current month.
    Fetches all expense documents from the Firestore collection within the current month,
    calculates the total amount spent, aggregates expenses by category, and retrieves
    the current month's budget. Returns the summary as a JSON string.
    Returns:
        str: A JSON string containing the total expenses, category-wise breakdown,
             list of expenses, and the current month's budget.
    """
    collection_ref = firestore_client.collection(EXPENSE_COLLECTION_NAME)
    today = datetime.now()
    docs = (
        await collection_ref.where(
            filter=FieldFilter("date", ">=", today.replace(day=1).isoformat())
        )
        .where(filter=FieldFilter("date", "<=", today.isoformat()))
        .get()
    )

    expenses = [
        ExpenseSchema(
            id=doc.id,
            **doc.to_dict(),
        )
        for doc in docs
    ]
    total = sum(expense.amount for expense in expenses)

    budget = await get_current_month_budget()

    categories = {}
    for expense in expenses:
        if expense.category not in categories:
            categories[expense.category] = 0.0
        categories[expense.category] += expense.amount

    return ExpenseSummaryOutputSchema(
        total=total,
        categories=categories,
        expenses=expenses,
        budget=budget,
    ).model_dump_json()


root_agent = Agent(
    name="expense_agent",
    model="gemini-2.5-flash",
    instruction=f"""You are ExpenseBot, a helpful financial assistant that helps users track their expenses and budget.
You can help users:
1. Add new expenses
2. Update or delete existing expenses
3. View their expense history
4. Set and view their monthly budget
5. Get a summary of their spending
6. Get all categories of expenses
7. Get expenses by category
8. Get expenses by date
9. Get all expenses
10. Get expenses by date range
11. Set Budget for a month -  Before setting a budget, check if the user has already set a budget for the month. If they have, ask them if they want to update it or set a new one.
Use can auto assign categories to expenses based on the name of the expense. For example, if the name of the expense is "Groceries", you can assign it to the "Food" category. But ask the user for confirmation before assigning the category.
When helping users with these tasks, guide them by asking for necessary information if it's missing.
Always use rupees (INR) as the currency.
{date_system_prompt()}""",
    tools=[
        add_expense,
        get_all_expenses,
        get_expense_by_date,
        get_expense_by_date_range,
        update_expense,
        delete_expense,
        get_expenses_by_category,
        get_all_categories,
        add_budget,
        get_current_month_budget,
        update_budget,
        delete_budget,
        get_expense_summary,
    ],
)
