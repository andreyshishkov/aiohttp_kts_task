import typing
from hashlib import sha256

from app.admin.models import Admin
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        # TODO: создать админа по данным в config.yml здесь
        admin_config = app.config.admin
        existing_admin = await self.get_by_email(admin_config.email)
        if not existing_admin:
            await self.create_admin(
                email=admin_config.email,
                password=admin_config.password
        )

    async def get_by_email(self, email: str) -> Admin | None:
        for admin in self.app.database.admins:
            if admin.email == email:
                return admin
        return None

    async def get_by_id(self, id_: int) -> Admin | None:
        for admin in self.app.database.admins:
            if admin.id == id_:
                return admin
        return None

    async def create_admin(self, email: str, password: str) -> Admin:
        hashed_password = sha256(password.encode()).hexdigest()

        admin = Admin(
            id=self.app.database.next_admin_id,
            email=email,
            password=hashed_password
        )

        self.app.database.admins.append(admin)

        return admin
