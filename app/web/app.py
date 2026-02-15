from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
    middleware
)
from aiohttp_session import session_middleware, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_apispec import setup_aiohttp_apispec
from cryptography import fernet
import base64

from app.admin.models import Admin
from app.store import Store, setup_store
from app.store.database.database import Database
from app.web.config import Config, setup_config
from app.web.logger import setup_logging
from app.web.middlewares import setup_middlewares
from app.web.routes import setup_routes


class Application(AiohttpApplication):
    config: Config | None = None
    store: Store | None = None
    database: Database = Database()


class Request(AiohttpRequest):
    admin: Admin | None = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


app = Application()


def setup_app(config_path: str) -> Application:
    setup_logging(app)
    setup_config(app, config_path)

    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    app.middlewares.append(session_middleware(EncryptedCookieStorage(secret_key)))

    setup_aiohttp_apispec(
        app=app,
        title="Quiz Bot API",
        version="1.0.0",
        url="/docs/swagger.json"
    )
    @middleware
    async def auth_middleware(request, handler):
        request.admin = None
        session = await get_session(request)
        admin_id = session.get("admin_id")
        if admin_id:
            admin = await app.store.admins.get_by_id(admin_id)
            request.admin = admin
        return await handler(request)

    app.middlewares.append(auth_middleware)

    setup_routes(app)
    setup_middlewares(app)
    setup_store(app)
    return app