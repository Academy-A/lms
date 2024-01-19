import csv
import io

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import StreamingResponse
from starlette_admin import HasOne, IntegerField, row_action

from lms.admin.views.models.base import BaseModelView
from lms.db.repositories.distribution import DistributionRepository
from lms.generals.models.distribution import Distribution


class DistributionModelView(BaseModelView):
    identity = "distribution"
    label = "Distribution"
    row_actions = ["download_soho_data", "download_distribution"]
    actions = []
    pydantic_model = Distribution

    fields = [
        IntegerField(name="id", label="ID", required=True),
        HasOne(
            name="subject",
            label="subject",
            identity="subject",
            required=True,
        ),
    ]

    @row_action(  # type: ignore[arg-type]
        name="download_soho_data",
        text="Download Soho homeworks as CSV",
        icon_class="fas fa-download",
        custom_response=True,
    )
    async def download_soho_data(
        self,
        request: Request,
        id: int,
    ) -> StreamingResponse:
        session: AsyncSession = request.state.session
        distribution = await DistributionRepository(session=session).read_by_id(int(id))
        dumped_distr = distribution_dump_to_csv_string(distribution)
        response = StreamingResponse(iter([dumped_distr]), media_type="text/csv")
        response.headers[
            "Content-Disposition"
        ] = f"attachment; filename=soho_homeworks_{id}.csv"
        return response

    @row_action(  # type: ignore[arg-type]
        name="download_distribution",
        text="Download whole distributioin as JSON",
        icon_class="fas fa-download",
        custom_response=True,
    )
    async def download_distribution_data(
        self,
        request: Request,
        id: int,
    ) -> ORJSONResponse:
        session: AsyncSession = request.state.session
        distribution = await DistributionRepository(session=session).read_by_id(int(id))
        return ORJSONResponse(distribution.data)


def distribution_dump_to_csv_string(distribution: Distribution) -> str:
    data = distribution.serialize_soho_homeworks()
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerows(data)
    return output.getvalue()
