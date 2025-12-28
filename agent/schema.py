from typing import List, Literal, Union, Optional
from pydantic import BaseModel,Field

class Click(BaseModel): 
    """Click at a specified (x, y) pixel coordinate on the screen"""
    type : Literal["click"]
    x: float = Field(..., description="x coordinate of screen")
    y: float = Field(..., description="y coordinate of screen") 
    button: Optional[Literal["left", "middle", "right"]] = Field(default="left", description="The button of the mouse for click action")

class Hover(BaseModel): 
    """Hover the cursor at a specified (x, y) pixel coordinate on the screen"""
    x: float = Field(..., description="x coordinate of screen")
    y: float = Field(..., description="y coordinate of screen") 

class Key(BaseModel): 
    """
    Performs key down presses on the arguments passed in order, then performs key releases in reverse order. Includes 'Enter', 'Alt', 'Shift', 'Tab', 'Control', 'Backspace', 'Delete', 'Escape', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'PageDown', 'PageUp', 'Shift', etc.
    """    
    keys: List[str]

class Type(BaseModel): 
    """Type a string of text on the keyboard. """
    type: Literal["type"]
    x: float = Field(..., description="x coordinate of screen")
    y: float = Field(..., description="y coordinate of screen") 
    text : str = Field(..., description="Text to type")
    press_enter: Optional[bool] = True
    clear_before_typing: Optional[bool] = True 

class Scroll(BaseModel): 
    """Performs a scroll of the mouse scroll wheel."""
    type : Literal["scroll"]
    x: int
    y: int
    direction: Literal["up", "down", "left", "right"]
    magnitude: int

class Wait(BaseModel): 
    """Wait specified seconds for the change to happen."""
    type : Literal["wait"]
    seconds: float = Field(..., ge=0)

class GoBack(BaseModel): 
    """Go back to the previous page in the browser history."""

class Search(BaseModel): 
    """Perform a web search with a specified query."""
    query: str = Field(..., description="")
    search_engine: Optional[Literal["google", "bing", "duckduckgo", "yahoo"]] = "google"

class Navigate(BaseModel): 
    """Visit a specified URL."""
    url: str

class DragAndDrop(BaseModel):
    """Represents a drag-and-drop mouse action using absolute screen coordinates."""
    x: int = Field(...,ge=0,description="Starting X-coordinate (in pixels) of the drag action.")
    y: int = Field(...,ge=0,description="Starting Y-coordinate (in pixels) of the drag action.")
    destination_x: int = Field(...,ge=0,description="Target X-coordinate (in pixels) where the item is dropped.")
    destination_y: int = Field(..., ge=0, description="Target Y-coordinate (in pixels) where the item is dropped.")

class Terminate(BaseModel):
    """Terminate the current task and report its completion status."""
    status: Literal["success", "failure"] = Field(..., description="Status of the task. Required only by action=terminate.")
    result: Optional[str] = Field(...,description="Final result or answer produced by the task, if applicable.")

Action = Union[
    Click,
    Hover,
    DragAndDrop,  
    Search,
    Type, 
    Scroll, 
    GoBack,
    Key,
    Navigate,
    Wait, 
    Terminate
]

class AgentStep(BaseModel):
    """Single agent reasoning-and-action step for the current state."""

    thought: str = Field(
        ...,
        description="Brief reasoning about the current screen and goal."
    )
    action: Action = Field(
        ...,
        description="Action to execute on the computer."
    )