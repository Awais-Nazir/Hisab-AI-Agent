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
    {
        "type": "function",
        "function": {
            "name": "propose_udhar",
            "description": (
                "Propose creating a new udhar entry. "
                "Use this when the user wants to record that they gave money "
                "to someone (LENA) or owe money to someone (DENA). "
                "This tool only creates a pending proposal and does NOT save "
                "anything to Hisab yet. "
                "You must resolve the person's ID using list_contacts and the "
                "account ID using list_accounts before calling this tool."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["LENA", "DENA"],
                        "description": (
                            "LENA means the user should receive money from the person. "
                            "DENA means the user owes money to the person."
                        ),
                    },
                    "person_id": {
                        "type": "string",
                        "description": "The contact/person ID from list_contacts.",
                    },
                    "amount": {
                        "type": "number",
                        "description": "The udhar amount in PKR.",
                    },
                    "account_id": {
                        "type": "string",
                        "description": "The account ID used for the udhar.",
                    },
                    "note": {
                        "type": "string",
                        "description": "Optional note for the udhar entry.",
                    },
                },
                "required": [
                    "type",
                    "person_id",
                    "amount",
                    "account_id",
                ],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "propose_expense",
            "description": (
                "Propose creating a new expense. "
                "Use this when the user wants to record an expense or purchase. "
                "This tool only creates a pending proposal and does NOT save "
                "anything to Hisab yet. "
                "You must resolve the category ID using list_categories and "
                "the account ID using list_accounts before calling this tool. "
                "For shared expenses, payments and splits must represent the "
                "full expense amount."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "The full expense amount in PKR.",
                    },
                    "description": {
                        "type": "string",
                        "description": "A short description of the expense.",
                    },
                    "category_id": {
                        "type": "string",
                        "description": "The category ID from list_categories.",
                    },
                    "account_id": {
                        "type": "string",
                        "description": "The account ID from list_accounts.",
                    },
                    "is_personal": {
                        "type": "boolean",
                        "description": (
                            "True if the expense is personal. "
                            "False if it is shared with other people."
                        ),
                    },
                    "payments": {
                        "type": "array",
                        "description": (
                            "How the full expense amount was paid. "
                            "Payment amounts must sum to the full expense amount."
                        ),
                        "items": {
                            "type": "object",
                            "properties": {
                                "person_id": {
                                    "type": "string",
                                    "description": "The person's ID.",
                                },
                                "amount": {
                                    "type": "number",
                                    "description": "Amount paid by this person.",
                                },
                            },
                            "required": ["person_id", "amount"],
                            "additionalProperties": False,
                        },
                    },
                    "splits": {
                        "type": "array",
                        "description": (
                            "How the expense is divided between people. "
                            "For shared expenses, split amounts must sum to "
                            "the full expense amount."
                        ),
                        "items": {
                            "type": "object",
                            "properties": {
                                "person_id": {
                                    "type": "string",
                                    "description": "The person's ID.",
                                },
                                "amount": {
                                    "type": "number",
                                    "description": "Amount assigned to this person.",
                                },
                            },
                            "required": ["person_id", "amount"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": [
                    "amount",
                    "description",
                    "category_id",
                    "account_id",
                    "is_personal",
                    "payments",
                ],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "propose_settlement",
            "description": (
                "Propose settling a shared-expense balance between the user and "
                "another person. This tool only creates a pending proposal and "
                "does NOT save anything to Hisab yet. "
                "Use this for shared-expense settlements, NOT for settling udhar. "
                "You must use list_contacts to resolve the person's ID and "
                "list_accounts if an account is needed. "
                "The payment direction is represented by from_person_id and "
                "to_person_id."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "from_person_id": {
                        "type": "string",
                        "description": (
                            "The person who is paying the settlement. "
                            "Use 'self' when the user is making the payment."
                        ),
                    },
                    "to_person_id": {
                        "type": "string",
                        "description": (
                            "The person receiving the settlement. "
                            "Use the contact ID from list_contacts."
                        ),
                    },
                    "amount": {
                        "type": "number",
                        "description": "The settlement amount in PKR.",
                    },
                    "account_id": {
                        "type": "string",
                        "description": (
                            "The account ID used for the settlement. "
                            "Required when the user specifies or needs an account."
                        ),
                    },
                    "note": {
                        "type": "string",
                        "description": "Optional note for the settlement.",
                    },
                },
                "required": [
                    "from_person_id",
                    "to_person_id",
                    "amount",
                ],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "propose_udhar_settle",
            "description": (
                "Propose settling an existing udhar entry. "
                "This tool only creates a pending proposal and does NOT save "
                "anything to Hisab yet. "
                "Use this only when the user explicitly wants to settle, "
                "clear, or mark an existing udhar as paid. "
                "You must first use list_udhar to find the udhar entry and "
                "its ID. You must use list_accounts to resolve the account "
                "ID if the user specifies an account or if an account is "
                "required for the settlement."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "udhar_id": {
                        "type": "string",
                        "description": (
                            "The ID of the existing udhar entry from list_udhar."
                        ),
                    },
                    "account_id": {
                        "type": "string",
                        "description": ("The account ID used for settling the udhar."),
                    },
                },
                "required": [
                    "udhar_id",
                    "account_id",
                ],
                "additionalProperties": False,
            },
        },
    },
]
