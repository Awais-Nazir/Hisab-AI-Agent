tools = [
    {
        "type": "function",
        "function": {
            "name": "get_balance",
            "description": "Get the current balance of a user.",
            "parameters": {
                "type": "object",
                "properties": {"contact_name": {"type": "string"}},
                "required": ["contact_name"],
            },
        },
    }
]
