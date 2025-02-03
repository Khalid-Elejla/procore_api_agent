from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
import pandas as pd

def PandasAgent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    A Pandas agent that can analyze and manipulate DataFrames based on natural language queries.
    
    Args:
        state (Dict[str, Any]): Current state containing messages and DataFrame
            Expected keys:
            - "messages": List of conversation messages
            - "df": pandas DataFrame to analyze
            
    Returns:
        Dict[str, Any]: Updated state with analysis results
    """
    
    # Extract the latest message and DataFrame from state
    messages = state.get("messages", [])
    df = state.get("df")
    
    if df is None:
        return {
            "messages": messages + [
                AIMessage(content="Error: No DataFrame found in state")
            ]
        }
    
    # Get the latest query from messages
    latest_message = messages[-1].content if messages else ""
    
    try:
        # Create pandas agent
        agent = create_pandas_dataframe_agent(
            ChatOpenAI(temperature=0, model="gpt-4"),
            df,
            verbose=True
        )
        
        # Execute the query
        result = agent.run(latest_message)
        
        # Update state with results
        return {
            "messages": messages + [
                AIMessage(content=result)
            ],
            "df": df  # Maintain DataFrame in state
        }
    except Exception as e:
        return {
            "messages": messages + [
                AIMessage(content=f"Error during analysis: {str(e)}")
            ],
            "df": df
        }

# Example usage in LangGraph
from langgraph.graph import StateGraph, END

# Define your graph
workflow = StateGraph()

# Add the PandasAgent node
workflow.add_node("pandas_analyzer", PandasAgent)

# Define edges
workflow.add_edge("pandas_analyzer", END)

# Compile the graph
app = workflow.compile()

# Example usage with state initialization
initial_state = {
    "messages": [
        HumanMessage(content="What is the average value in column 'A'?")
    ],
    "df": pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
}

# Run the graph
result = app.invoke(initial_state)