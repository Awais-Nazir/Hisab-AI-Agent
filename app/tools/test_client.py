from .api_client import HisabClient


client = HisabClient()

try:
    login_result = client.login()
    print("Logged in:", login_result["user"])
    # expenses = client.list_expenses()
    # people = client.list_contacts()

    # print("#" * 19)
    # print(expenses)
    # print("#" * 19)
    # print("Peopel:")
    # print(people)

    # balance = client.list_contact_balance(people.get("people")[0]["id"])
    categories = client.list_categories()
    accounts = client.list_accounts()
    print(categories)
    print(accounts)

finally:
    client.close()
