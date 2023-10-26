from starlette_admin.contrib.sqla import ModelView


class SohoModelView(ModelView):
    form_include_pk = True
    fields = ["id", "email", "student"]
