tools = [
    {
        "type": "function",
        "function": {
            "name": "list_expenses",
            "description": (
                "Get the user's expenses. "
                "Use this when the user asks about their expenses, "
                "spending, purchases, or what they spent."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_contacts",
            "description": (
                "Get the user's contacts. "
                "Use this when you need to find a contact by name, "
                "resolve a person's ID, or see which people are available."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_contact_balance",
            "description": (
                "Get the current balance between the user and a specific contact. "
                "Use this when the user asks how much they owe a contact or how much "
                "a contact owes them. You must first use list_contacts to find the "
                "contact ID if you do not already have it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_id": {
                        "type": "string",
                        "description": "The contact ID returned by list_contacts.",
                    }
                },
                "required": ["contact_id", "contact_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_categories",
            "description": (
                "Get all expense categories available to the user. "
                "Use this when you need to find a category by name "
                "or resolve a category name to its ID before creating an expense."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_accounts",
            "description": (
                "Get all accounts belonging to the user. "
                "Use this whenever the user asks about their accounts, "
                "including asking for an account's ID, name, type, or balance. "
                "Use it to resolve an account name such as 'Bank Account', "
                "'Cash', 'NayaPay', or 'SadaPay' to its ID."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
]
