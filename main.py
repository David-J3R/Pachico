import sys

# sys is used to check command-line arguments to determine whether to run the CLI or the API server.
# example: `python main.py cli` will run the CLI, while `python main.py` will run the API server.


def main():
    # if the first command-line argument is "cli", run the CLI; otherwise, run the API server
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        from App.cli.cli import run_cli

        run_cli()
    else:
        # Lazy imports to speed up CLI startup time
        import uvicorn

        uvicorn.run("App.api:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
