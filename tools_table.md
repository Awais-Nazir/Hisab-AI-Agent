| Agent Tool | What it does | Main inputs | Type | Hisab API |
|---|---|---|---|---|
| `propose_expense` | Proposes a personal **or shared** expense | amount, description, payer, participants/splits, account, date | **Write** | `POST /api/expenses` or `/api/expenses/personal` |
| `get_expenses` | Gets existing expenses for understanding/calculations | filters, date range, person, category, account | **Read** | `GET /api/expenses` |
| `get_person_balance` | Gets someone's **net shared-expense balance** — who owes whom | person ID | **Read** | `GET /api/people/[id]/ledger` |
| `propose_udhar` | Records money borrowed/lent separately from shared expenses | person, amount, `LENA`/`DENA`, account, note, date | **Write** | `POST /api/udhar` |
| `propose_settlement` | Proposes settling an Udhar/shared-person balance | person/entry, amount, account | **Write** | `POST /api/udhar/[id]/settle` |
| `get_accounts` | Gets user's wallets/accounts and current balances | — | **Read** | `GET /api/accounts` |
| `propose_transfer` | Transfers money between user's own accounts | from account, to account, amount, note, date | **Write** | `POST /api/accounts/transfer` |
| `propose_deposit` | Adds money directly into an account, e.g. salary | account, amount, description, date | **Write** | `POST /api/accounts/[id]/deposit` |
| `find_person` | read tool that returns matching people with their IDs. | person name | **Read** | `GET /api/people` |