import uvicorn

from main import app


def main() -> None:
    """Run the API server entry point used by validator and packaging scripts."""
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
