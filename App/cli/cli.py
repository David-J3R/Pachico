from App.service import invoke_agent


def run_cli() -> None:
    print("Pachico CLI — type 'quit' to exit")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break

            response = invoke_agent(user_input, "cli-1")
            print(f"Assistant: {response.text}")

            for path in response.file_paths:
                print(f"  [File] {path}")

        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
