import typing
from hashlib import sha256

from app.admin.models import Admin
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        # TODO: создать админа по данным в config.yml здесь
        await self.app.store.admins.create_admin(
            email=self.app.config.admin.email,
            password=self.app.config.admin.password
        )

    async def get_by_email(self, email: str) -> Admin | None:
        for admin in self.app.database.admins:
            if admin.email == email:
                return admin
        return None

    async def create_admin(self, email: str, password: str) -> Admin:
        passw = sha256(password.encode()).hexdigest()
        admin = Admin(
            id=self.app.database.next_admin_id,
            email=email,
            password=passw,
        )
        self.app.database.admins.append(admin)
        return admin
