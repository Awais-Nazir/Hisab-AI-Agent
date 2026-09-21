from app.tools.read import list_accounts, list_categories, list_expenses
from app.tools.read import list_contacts, get_contact_balance


result = list_expenses()

peoples = list_contacts()
# print(peoples)
net_balance = get_contact_balance(
    peoples["people"][0]["id"], peoples["people"][0]["name"]
)

categories = list_categories()
accounts = list_accounts()

# print(result)
print(accounts)
