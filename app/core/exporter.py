"""Create in-memory Excel and CSV backups from the local database."""

from io import BytesIO, StringIO

import pandas as pd

from app.core.constants import TABLE_COLUMNS
from app.core.db import fetch_all


def export_excel(connection) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for table, columns in TABLE_COLUMNS.items():
            frame = pd.DataFrame(fetch_all(connection, table), columns=columns)
            frame.to_excel(writer, sheet_name=table[:31], index=False)
        settings = pd.DataFrame(
            [{"key": key, "value": value} for key, value in connection.execute(
                "SELECT key, value FROM settings"
            )]
        )
        settings.to_excel(writer, sheet_name="settings", index=False)
    return output.getvalue()


def export_csv(connection, table: str) -> str:
    if table not in TABLE_COLUMNS:
        raise ValueError(f"Unsupported table: {table}")
    output = StringIO()
    pd.DataFrame(fetch_all(connection, table), columns=TABLE_COLUMNS[table]).to_csv(
        output, index=False
    )
    return output.getvalue()
