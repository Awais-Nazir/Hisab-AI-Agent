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
    # categories = client.list_categories()
    # category_id = "cmua98y6g0001jp04pd82u2t4"

    # category_name = client.get_category_name(category_id)

    # print("Category:", category_name)
    # accounts = client.list_accounts()
    # udhar = client.list_udhar()
    # print(udhar)
    # print(categories)
    # print(accounts)

    # result = client.write_expense(
    #     amount=100,
    #     description="AI Agent test expense",
    #     category="Food & Dining",
    #     account_id="cmu8poi7z0001jw04yr0glune",
    #     is_personal=True,
    # )

    # result = client.write_udhar(
    #     type="LENA",
    #     person_id="cmua0yfv70003jp04bir7vobp",
    #     amount=2500,
    #     account_id="cmu8poi7z0001jw04yr0glune",
    #     note="Lent for fuel",
    #     # "date"= "2026-09-19T12:00:00.000Z"
    # )

    result = client.settle_udhar(
        udhar_id="cmulqh0sk0001kz040fis7a1g", account_id="cmu8poi7z0000jw04h0c1xx8z"
    )
    print(result)


finally:
    client.close()
