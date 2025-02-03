from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from typing import List
from langchain.tools import BaseTool
from .db_query_tool import CustomQuerySQLDataBaseTool
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from .dataframe_manager import DataFrameManager

# df_manager=DataFrameManager()

class CustomSQLDatabaseToolkit(SQLDatabaseToolkit):

    # def get_tools(self) -> List[BaseTool]:
    
    def get_tools(self, df_manager) -> List[BaseTool]:
        """Get the tools in the toolkit with custom query tool."""
        # df_manager = DataFrameManager()
        tools = super().get_tools()

        # Replace the default QuerySQLDataBaseTool with our custom one
        tools = [
            CustomQuerySQLDataBaseTool(db=self.db, description=t.description, df_manager=df_manager) 
            if isinstance(t, QuerySQLDataBaseTool) 
            else t 
            for t in tools
        ]

        return tools