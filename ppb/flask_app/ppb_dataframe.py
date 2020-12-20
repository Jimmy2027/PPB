import typing
from pathlib import Path

import pandas as pd

from ppb.logger.logger import log


def update_ppb_dataframe_post(values: typing.Mapping[str, any]) -> None:
    df_path = Path(__file__).parent.parent / 'ppd_dataframe.csv'
    if not df_path.exists():
        df = pd.DataFrame([values])
    else:
        df = pd.read_csv(df_path)
        filename = values['filename']
        df = df[df['filename'] != filename]

        df = df.append(values, ignore_index=True)
    df.to_csv(df_path, index=False)


def update_ppb_dataframe_get(values: typing.Mapping[str, any], filename: str) -> None:
    """
    Updates the ppb_datafram on GET request.
    """
    df_path = Path(__file__).parent.parent / 'ppd_dataframe.csv'

    if df_path.exists():
        # if filename in
        df = pd.read_csv(df_path)
        if not df.empty and filename in df['filename']:
            log.info(df.loc[df['filename'] == filename])
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
