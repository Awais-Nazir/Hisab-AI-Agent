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
                "Get the shared-expense balance between the user and a specific contact. "
                "This balance comes from shared expenses and settlements, NOT udhar entries. "
                "Use this when the user asks how much they owe someone or how much someone "
                "owes them from shared expenses. Do NOT use this for questions explicitly "
                "about udhar, lena, dena, or udhar entries. "
                "You must first use list_contacts to find the contact ID if you do not already have it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_id": {
                        "type": "string",
                        "description": "The contact ID returned by list_contacts.",
                    }
                },
                "required": ["contact_id"],
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
    {
        "type": "function",
        "function": {
            "name": "list_udhar",
            "description": (
                "Get the user's udhar entries. "
                "Use this for questions about udhar, lena, dena, loans, or money "
                "owed outside the shared-expense balance. "
                "If the user mentions a person's name, use the returned person_name "
                "and type to find that person's udhar. "
                "LENA means the user has given money and should receive it back. "
                "DENA means the user owes money to that person. "
                "Do NOT use get_contact_balance for explicit udhar questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
]
