import csv
import io

from fastapi.responses import ORJSONResponse
from sqladmin import action
from starlette.requests import Request
from starlette.responses import StreamingResponse

from lms.adapters.db.models import Distribution as DistributionDb
from lms.adapters.db.repositories.distribution import DistributionRepository
from lms.generals.models.distribution import Distribution
from lms.presentation.rest.admin.utils import format_datetime_field
from lms.presentation.rest.admin.views.base import AdminCategories, BaseModelView


class DistributionModelView(BaseModelView, model=DistributionDb):
    category = AdminCategories.MODELS
    can_create = False
    column_list = [
        DistributionDb.id,
        DistributionDb.subject,
        DistributionDb.created_at,
        DistributionDb.updated_at,
    ]
    column_sortable_list = [
        DistributionDb.id,
        DistributionDb.created_at,
        DistributionDb.updated_at,
    ]
    column_default_sort = ("created_at", True)
    column_formatters = {
        DistributionDb.created_at: format_datetime_field,
        DistributionDb.updated_at: format_datetime_field,
    }
    column_searchable_list = [
        DistributionDb.id,
        "subject.name",
    ]
    column_details_list = []

    @action(
        name="download_soho_data",
        label="Download Soho homeworks as CSV",
        add_in_detail=False,
        add_in_list=True,
    )
    async def download_soho_data(self, request: Request) -> StreamingResponse:
        pk = request.query_params.get("pks")
        if pk is None:
            raise ValueError
        id = int(pk)
        async with self.session_maker() as session:
            distribution = await DistributionRepository(session=session).read_by_id(id)
        dumped_distr = distribution_dump_to_csv_string(distribution)
        response = StreamingResponse(iter([dumped_distr]), media_type="text/csv")
        response.headers["Content-Disposition"] = (
            f"attachment; filename=soho_homeworks_{id}.csv"
        )
        return response

    @action(
        name="download_distribution_data",
        label="Download distribution homeworks as JSON",
        add_in_detail=False,
        add_in_list=True,
    )
    async def download_distribution_data(self, request: Request) -> ORJSONResponse:
        pk = request.query_params.get("pks")
        if pk is None:
            raise ValueError
        id = int(pk)
        async with self.session_maker() as session:
            distribution = await DistributionRepository(session=session).read_by_id(id)
        return ORJSONResponse(distribution.data)


def distribution_dump_to_csv_string(distribution: Distribution) -> str:
    data = distribution.serialize_soho_homeworks()
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerows(data)
    return output.getvalue()
