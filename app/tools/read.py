from .api_client import HisabClient


client = HisabClient()
client.login()


def list_expenses():
    data = client.list_expenses()

    expenses = []

    for expense in data.get("expenses", []):
        expenses.append({
            "amount": expense["amount"],
            "description": expense["description"],
            "category": expense["category"],
            "date": expense["date"],
            "account": (expense["account"]["name"] if expense.get("account") else None),
            "personal": expense["isPersonal"],
            "your_share": expense["userShare"],
            "you_paid": expense["userPaid"],
            "split_with": [
                person["name"]
                for person in expense.get("splitWith", [])
                if not person.get("isSelf")
            ],
        })

    meta = data.get("meta", {})

    return {
        "expenses": expenses,
        "total_count": meta.get("totalCount", 0),
        "total_amount": meta.get("totalAmount", 0),
        "total_your_share": meta.get("totalUserShare", 0),
        "total_you_paid": meta.get("totalUserPaid", 0),
    }


def list_contacts():
    data = client.list_contacts()

    people = []

    for person in data.get("people", []):
        people.append({
            "id": person["id"],
            "name": person["name"],
        })

    return {
        "people": people,
    }


def get_contact_balance(contact_id):
    data = client.list_contact_balance(contact_id)

    balance = data.get("total", 0)

    if balance < 0:
        direction = "you_owe"
        amount = abs(balance)
    elif balance > 0:
        direction = "they_owe_you"
        amount = balance
    else:
        direction = "settled"
        amount = 0

    return {
        "contact_id": contact_id,
        "balance": balance,
        "amount": amount,
        "direction": direction,
        "total_expenses_count": data.get("totalExpensesCount", 0),
        "total_settlements_count": data.get("totalSettlementsCount", 0),
    }


def list_categories():
    data = client.list_categories()

    categories = []

    for category in data.get("categories", []):
        categories.append({
            "id": category["id"],
            "name": category["name"],
        })

    return {
        "categories": categories,
    }


def list_accounts():
    data = client.list_accounts()

    accounts = []

    for account in data.get("accounts", []):
        accounts.append({
            "id": account["id"],
            "name": account["name"],
            "type": account["type"],
            "balance": int(account["balance"]),
        })

    return {
        "accounts": accounts,
    }


def list_udhar():
    data = client.list_udhar()

    entries = []

    for entry in data.get("entries", []):
        entries.append({
            "id": entry["id"],
            "person_id": entry["personId"],
            "person_name": entry["person"]["name"],
            "type": entry["type"],
            "amount": float(entry["amount"]),
            "note": entry.get("note"),
            "date": entry["date"],
            "is_settled": entry["isSettled"],
        })

    return {
        "entries": entries,
    }
