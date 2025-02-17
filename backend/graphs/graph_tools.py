from __future__ import annotations
from langgraph.prebuilt import ToolNode

from copy import copy

from langchain_core.runnables import RunnableConfig

from langchain_core.runnables.utils import Input


from langgraph.store.base import BaseStore

import asyncio

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    cast,
)

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    ToolCall,
    ToolMessage,
)
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.config import (
    get_config_list,
    get_executor_for_config,
)
from langchain_core.runnables.utils import Input
from langchain_core.tools import BaseTool, InjectedToolArg
from langchain_core.tools import tool as create_tool
from typing_extensions import Annotated, get_args, get_origin

from langgraph.store.base import BaseStore
from langgraph.utils.runnable import RunnableCallable

from pydantic import BaseModel



# def custom_tools_condition(
#     state: Union[list[AnyMessage], dict[str, Any], BaseModel],
# ) -> Literal["tools", "__end__"]:
    
#     if isinstance(state, list):
#         ai_message = state[-1]
#     elif isinstance(state, dict) and (messages := state.get("sql_agent_messages", [])):
#         ai_message = messages[-1]
#     elif messages := getattr(state, "sql_agent_messages", []):
#         ai_message = messages[-1]
#     else:
#         raise ValueError(f"No messages found in input state to tool_edge: {state}")
#     if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
#         return "tools"
#     return "__end__"

def custom_tools_condition(  
    state: Union[list[AnyMessage], dict[str, Any], BaseModel],  
    message_key: str = "messages",  
) -> Literal["tools", "__end__"]:  

    if isinstance(state, list):  
        ai_message = state[-1]  
    elif isinstance(state, dict) and (messages := state.get(message_key, [])):  
        ai_message = messages[-1]  
    elif messages := getattr(state, message_key, []):  
        ai_message = messages[-1]  
    else:  
        raise ValueError(f"No messages found in input state to tool_edge: {state}")  
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:  
        return "tools"  
    return "__end__"

# class SQLToolNode(ToolNode):  
#     """Specialized ToolNode for SQL operations"""  

#     def _parse_input(  
#         self,  
#         input: Union[  
#             list[AnyMessage],  
#             dict[str, Any],  
#             BaseModel,  
#         ],  
#         store: BaseStore,  
#     ) -> Tuple[List[ToolCall], Literal["list", "dict"]]:  
#         if isinstance(input, list):  
#             output_type = "list"  
#             message = input[-1]  
#         elif isinstance(input, dict):  
#             output_type = "dict"  
#             # Check sql_agent_messages first  
#             messages = input.get("sql_agent_messages", []) or input.get("messages", [])  
#             message = messages[-1] if messages else None  
#         elif messages := getattr(input, "messages", None):  
#             output_type = "dict"  
#             message = messages[-1]  
#         else:  
#             raise ValueError("No message found in input")  

#         if not isinstance(message, AIMessage):  
#             raise ValueError("Last message is not an AIMessage")  

#         tool_calls = [  
#             self._inject_tool_args(call, input, store) for call in message.tool_calls  
#         ]  
#         return tool_calls, output_type  

#     def _func(self, input: Union[list[AnyMessage], dict[str, Any], BaseModel],  
#               config: RunnableConfig,  
#               *,  
#               store: BaseStore,  
#     ) -> Any:  
#         outputs = super()._func(input, config, store=store)  
#         # Modify the output to use sql_agent_messages instead of messages  
#         if isinstance(outputs, dict) and "messages" in outputs:  
#             return {"sql_agent_messages": outputs["messages"]}  
#         return outputs  
    
class CustomToolNode(ToolNode): 
    """Flexible ToolNode for different message storage keys"""  

    def __init__(self, *args, message_key: str = "messages", **kwargs):  
        super().__init__(*args, **kwargs)  
        self.message_key = message_key  

    def _parse_input(  
        self,  
        input: Union[  
            list[AnyMessage],  
            dict[str, Any],  
            BaseModel,  
        ],  
        store: BaseStore,  
    ) -> Tuple[List[ToolCall], Literal["list", "dict"]]:  
        if isinstance(input, list):  
            output_type = "list"  
            message = input[-1]  
        elif isinstance(input, dict):  
            output_type = "dict"  
            # Check specified message_key first, then fall back to "messages"  
            messages = input.get(self.message_key, []) or input.get("messages", [])  
            message = messages[-1] if messages else None  
        elif messages := getattr(input, "messages", None):  
            output_type = "dict"  
            message = messages[-1]  
        else:  
            raise ValueError("No message found in input")  

        if not isinstance(message, AIMessage):  
            raise ValueError("Last message is not an AIMessage")  

        tool_calls = [  
            self.inject_tool_args(call, input, store) for call in message.tool_calls  
        ]  
        return tool_calls, output_type  

    def _func(  
        self,  
        input: Union[list[AnyMessage], dict[str, Any], BaseModel],  
        config: RunnableConfig,  
        *,  
        store: BaseStore,  
    ) -> Any:  
        outputs = super()._func(input, config, store=store)  
        # Modify the output to use the specified message_key instead of messages  
        if isinstance(outputs, dict) and "messages" in outputs:  
            return {self.message_key: outputs["messages"]}  
        return outputs