from app.tools.read import list_accounts, list_categories, list_expenses, list_udhar
from app.tools.read import list_contacts, get_contact_balance


result = list_expenses()

peoples = list_contacts()
# print(peoples)
net_balance = get_contact_balance(peoples["people"][0]["id"])

categories = list_categories()
accounts = list_accounts()
udhar = list_udhar()

# print(result)
print(udhar)
