from app.web.app import View
from app.web.utils import json_response
from app.admin.schemes import AdminSchema, AdminLoginSchema
from aiohttp_apispec import request_schema, response_schema
from aiohttp.web_exceptions import HTTPForbidden, HTTPUnauthorized
from aiohttp_session import new_session
from hashlib import sha256
class AdminLoginView(View):
    @request_schema(AdminLoginSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        email = self.data["email"]
        password = self.data["password"]

        admin = await self.store.admins.get_by_email(email)

        if not admin or admin.password != sha256(password.encode()).hexdigest():
            raise HTTPForbidden(reason="Invalid credentials")

        session = await new_session(self.request)
        session["admin_id"] = admin.id

        return json_response(data=AdminSchema().dump(admin))


class AdminCurrentView(View):
    @response_schema(AdminSchema, 200)
    async def get(self):
        if not self.request.admin:
            raise HTTPUnauthorized(reason="Authentication required")

        return json_response(data=AdminSchema().dump(self.request.admin))
