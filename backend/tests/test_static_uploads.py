from pathlib import Path

from fastapi.staticfiles import StaticFiles

from app.main import app


def test_uploads_directory_is_mounted() -> None:
    mounted_routes = {
        route.path: route
        for route in app.routes
        if hasattr(route, "app")
    }

    assert "/uploads" in mounted_routes
    assert isinstance(
        mounted_routes["/uploads"].app,
        StaticFiles,
    )


def test_uploads_directory_exists() -> None:
    assert Path("uploads").exists()
    assert Path("uploads").is_dir()