import typing
from pathlib import Path

import pandas as pd

from ppb.logger.logger import log
import numpy as np
import json
import os

DF_PATH = Path(__file__).parent.parent / 'ppd_dataframe.csv'


def update_ppb_dataframe_post(values: dict, file_path: Path) -> None:
    metadata = get_metadata(file_path)
    values = {**values, **metadata}
    df_path = DF_PATH

    # todo search for all files in static path and add them to df, set lifetime to 7

    if not df_path.exists():
        df = pd.DataFrame([values])
    else:
        df = pd.read_csv(df_path)
        filename = values['filename']
        df = df[df['filename'] != filename]

        df = df.append(values, ignore_index=True)

    df.to_csv(df_path, index=False)


def get_metadata(file_path: Path):
    """
    Reads metadata from metadata file and deletes it.
    """
    metadata_path = file_path.with_suffix('.json')
    log.info(f'reading metadata file {metadata_path}')
    with open(metadata_path) as json_file:
        metadata = json.load(json_file)
    log.info(f'Deleting metadata file {metadata_path}')
    os.remove(metadata_path)
    return metadata


def update_seen_by(df_row, ip_address: str) -> str:
    log.info(df_row)
    if df_row['seen_by'].isnull().values.any():
        return df_row['sender'].item()
    sep = ', '
    spl = df_row['seen_by'].item().split(sep)
    current_ips = {f'{ip}' for ip in spl}
    current_ips.add(ip_address)
    return sep.join(list(current_ips))


def update_ppb_dataframe_get(values: typing.Mapping[str, any], filename: str, ip_address: str) -> None:
    """
    Updates the ppb_dataframe on GET request.
    """
    df_path = DF_PATH
    log.info(f'updating ppb_dataframe for file {filename}.')
    if df_path.exists():
        df = pd.read_csv(df_path)
        if not df.empty and filename in df['filename'].tolist():
            log.info(df.loc[df['filename'] == filename])
            if 'seen_by' not in df.columns:
                df['seen_by'] = np.nan

            df.loc[df['filename'] == filename, 'seen_by'] = update_seen_by(df.loc[df['filename'] == filename],
                                                                           ip_address=ip_address)
            if 'view_counts' not in df.loc[df['filename'] == filename].columns \
                    or any(df.loc[df['filename'] == filename, 'view_counts'].isna()):
                df.loc[df['filename'] == filename, 'view_counts'] = 1
            else:
                log.debug('Adding to view counts!')
                df.loc[df['filename'] == filename, 'view_counts'] += 1
            log.info(f"Setting view count to {df.loc[df['filename'] == filename, 'view_counts']}")

            for k, v in values.items():
                df.loc[df['filename'] == filename, k] = v
            df.to_csv(df_path, index=False)
        else:
            log.info(f'{filename} not found in ppb_dataframe.')

    else:
        log.info(f'{df_path} not found')
