from starlette_admin.contrib.sqla import ModelView


class StudentModelView(ModelView):
    fields = ["id", "first_name", "last_name", "vk_id", "created_at", "updated_at"]
    exclude_fields_from_create = ["created_at", "updated_at"]
