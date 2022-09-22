import fastapi
from router import text, model, text_result, sources

app = fastapi.FastAPI(title="Texts API", version="0.1.0", description="API for DB",)
app.include_router(text.router)
app.include_router(model.router)
app.include_router(text_result.router)
app.include_router(sources.router)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
