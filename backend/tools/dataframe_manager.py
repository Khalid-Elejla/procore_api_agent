import pandas as pd
import uuid

class DataFrameManager:
    def __init__(self):
        self.dataframes = {}  # Store DataFrames in memory

    def store_df(self, df: pd.DataFrame) -> str:
        """Store DataFrame in memory and return its ID."""
        df_id = str(uuid.uuid4())  # Generate a unique ID
        self.dataframes[df_id] = df
        return df_id

    def get_df(self, df_id: str) -> pd.DataFrame:
        """Retrieve DataFrame by ID."""
        return self.dataframes.get(df_id)

    def cleanup(self, df_id: str):
        """Remove DataFrame from memory."""
        if df_id in self.dataframes:
            del self.dataframes[df_id]
