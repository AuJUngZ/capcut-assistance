from pathlib import Path


def validate_contiguous_target_ranges(segments: list[dict]) -> list[str]:
    errors: list[str] = []
    cursor_us = 0
    for index, segment in enumerate(segments):
        target = segment["target_timerange"]
        if target["start"] != cursor_us:
            errors.append(f"segment timeline is not contiguous at index {index}")
        cursor_us = target["start"] + target["duration"]
    return errors


def validate_material_paths_exist(paths: list[str]) -> list[str]:
    return [path for path in paths if not Path(path).exists()]
