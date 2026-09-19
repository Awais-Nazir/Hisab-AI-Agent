FAKE_BALANCES = {
    "Razaq": 1250,
    "Kaif": -450,
    "Ahmed": 3200,
}


def get_balance(contact_name: str):
    return {
        "contact_name": contact_name,
        "balance": FAKE_BALANCES.get(contact_name, 0),
    }
