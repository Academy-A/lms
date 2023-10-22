def get_cleaned_folder_ids(folder_ids: str) -> list[str]:
    return list(
        filter(
            lambda x: bool(x),
            map(lambda x: x.strip(), folder_ids.split("\n")),
        )
    )
