from fastapi import FastAPI


def test_app_instance() -> None:
    from app.main import app

    assert isinstance(app, FastAPI)
