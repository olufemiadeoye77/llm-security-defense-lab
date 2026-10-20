
"""
LLM Security Defense Lab
Version 0.1 — Local Python prototype

Uses invented records and harmless mock tools only.
This is an educational demonstration, not production security software.
"""

from dataclasses import dataclass


@dataclass
class User:
    user_id: str
    role: str


# Invented customer records. No real customer data.
CUSTOMERS = {
    "C001": {
        "name": "Ada Demo",
        "department": "Sales",
        "classification": "standard",
    },
    "C002": {
        "name": "Bola Sample",
        "department": "Finance",
        "classification": "restricted",
    },
    "C003": {
        "name": "Chidi Example",
        "department": "Operations",
        "classification": "standard",
    },
}

# Explicit allowlist of harmless demonstration tools.
MOCK_TOOLS = {
    "list_customers": {"analyst", "support", "admin"},
    "view_standard_record": {"analyst", "support", "admin"},
    "view_restricted_record": {"admin"},
    "generate_demo_report": {"analyst", "admin"},
}


def validate_input(value: str) -> str:
    """Reject empty or excessively long input."""
    value = value.strip()

    if not value:
        raise ValueError("Input cannot be empty.")

    if len(value) > 200:
        raise ValueError("Input is too long (maximum 200 characters).")

    return value


def authorize(user: User, tool_name: str) -> bool:
    """Check that a tool exists and the user's role is permitted."""
    allowed_roles = MOCK_TOOLS.get(tool_name)

    if allowed_roles is None:
        return False

    return user.role in allowed_roles


def execute_mock_tool(user: User, tool_name: str) -> str:
    """Execute an allowlisted demonstration action."""
    if not authorize(user, tool_name):
        return f"BLOCKED: role '{user.role}' cannot use '{tool_name}'."

    if tool_name == "list_customers":
        return "Demo record IDs: " + ", ".join(CUSTOMERS.keys())

    if tool_name == "view_standard_record":
        return str({
            key: record["name"]
            for key, record in CUSTOMERS.items()
            if record["classification"] == "standard"
        })

    if tool_name == "view_restricted_record":
        # The restricted record is shown only after authorization.
        return str({
            key: record
            for key, record in CUSTOMERS.items()
            if record["classification"] == "restricted"
        })

    if tool_name == "generate_demo_report":
        return (
            f"Demo report: {len(CUSTOMERS)} synthetic records loaded. "
            "No external systems were contacted."
        )

    return "BLOCKED: unknown tool."


def main():
    print("=" * 48)
    print("LLM SECURITY DEFENSE LAB — LOCAL PROTOTYPE")
    print("=" * 48)
    print("Use invented data only. No real tools are connected.\n")

    print("Choose a demo role:")
    print("1. Analyst")
    print("2. Support")
    print("3. Admin")

    roles = {"1": "analyst", "2": "support", "3": "admin"}
    choice = input("Enter 1, 2, or 3: ").strip()

    if choice not in roles:
        print("Invalid role selection.")
        return

    user = User(user_id="demo-user", role=roles[choice])

    print(f"\nSigned in with demo role: {user.role}")
    print("\nAvailable actions:")
    print("1. List synthetic customer IDs")
    print("2. View standard records")
    print("3. View restricted records")
    print("4. Generate a demo report")
    print("5. Exit")

    actions = {
        "1": "list_customers",
        "2": "view_standard_record",
        "3": "view_restricted_record",
        "4": "generate_demo_report",
    }

    while True:
        try:
            command = validate_input(input("\nChoose an action (1-5): "))
        except ValueError as error:
            print(f"Input rejected: {error}")
            continue

        if command == "5":
            print("Session ended.")
            break

        if command not in actions:
            print("Invalid action. Choose 1, 2, 3, 4, or 5.")
            continue

        tool_name = actions[command]
        result = execute_mock_tool(user, tool_name)

        print(f"\nAction: {tool_name}")
        print(f"Result: {result}")


if __name__ == "__main__":
    main()
