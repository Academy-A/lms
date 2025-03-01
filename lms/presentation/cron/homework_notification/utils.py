import aiomisc
from google_api_service_helper import GoogleDrive
from google_api_service_helper.drive.schemas import FileResponse


def get_cleaned_folder_ids(folder_ids: str) -> list[str]:
    return list(
        filter(
            lambda x: bool(x),
            map(lambda x: x.strip(), folder_ids.split("\n")),
        )
    )


@aiomisc.threaded
def get_google_folder_files_recursively(
    google_drive: GoogleDrive, folder_id: str
) -> list[FileResponse]:
    return google_drive.get_all_folder_files_recursively(folder_id=folder_id)
