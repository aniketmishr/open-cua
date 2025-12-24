# Agent Implementation using openai 
import asyncio
from openai import OpenAI
from utils.prompts import OS_SYSTEM_PROMPT
from typing import List, Dict, Literal, Union
from pydantic import BaseModel, Field
from computer.playwright import PlaywrightComputer, ComputerState
import os, tempfile
from dotenv import load_dotenv

load_dotenv()
MODEL = "gpt-5-mini"


# Structured Output
class ClickAction(BaseModel): 
    type : Literal["click"]
    x: float = Field(..., description="x coordinate of screen")
    y: float = Field(..., description="y coordinate of screen") 

class TypeAction(BaseModel): 
    type: Literal["type"]
    text : str = Field(..., description="Text to type")

class ScrollAction(BaseModel): 
    type : Literal["scroll"]
    x: int
    y: int
    direction: Literal["up", "down", "left", "right"]
    magnitude: int

class WaitAction(BaseModel): 
    type : Literal["wait"]
    seconds: float = Field(..., ge=0)

class DoneAction(BaseModel): 
    type : Literal["done"]

Action = Union[
    ClickAction, 
    TypeAction, 
    ScrollAction, 
    WaitAction, 
    DoneAction
]

class CUAOutput(BaseModel): 
    thought : str = Field(..., description="Short reasoning about the current screen and goal")
    actions : List[Action] = Field(..., 
                                   min_length= 1,
                                   description="Ordered list of actions to execute sequentially")

client = OpenAI()


def create_response(messages:List[Dict]): 
    response = client.chat.completions.parse(
        model=MODEL, 
        messages=messages, 
        response_format=CUAOutput
    )
    return response.choices[0].message.parsed # return pydantic object CUAOutput

async def execute_actions(agent_output: CUAOutput, computer: PlaywrightComputer) -> Union[ComputerState, str]:
    """
    Execute a single parsed action on the computer.
    """
    for action in agent_output.actions: 
        # screen_width, screen_height = computer.get_dimensions() 

        if action.type== "click":
            state = await computer.click_at(action.x, action.y)

        # elif action_type == "double_click":
        #     computer.double_click(action_param["x"]*screen_width, action_param["y"]*screen_height)

        elif action.type == "type":
            state = await computer.type_text(text=action.text)

        elif action.type == "scroll":
            state = await computer.scroll_at(
                action.x, 
                action.y, 
                action.direction, 
                action.magnitude       # Computer Scroll takes diff. input format TODO('fix paramenter mismatch')
            )

        elif action.type == "wait":
            state = await computer.wait(action.seconds)

        elif action.type == "done":
            return "done"

        else:
            raise ValueError(f"Unknown action: {action}")

    return state

async def get_playwright_instance(): 
    # Initialize playwright computer instance
    # Define user_data_dir path
    profile_name = 'browser_profile_for_cua'
    profile_path = os.path.join(tempfile.gettempdir(), profile_name)
    os.makedirs(profile_path, exist_ok=True)

    p = PlaywrightComputer(
        screen_size=(936, 684),
        user_data_dir=profile_path,
        highlight_mouse=True
    ) 
    await p.initialize()
    await asyncio.sleep(3)  # TODO(TO REMOVE)
    return p


async def cua_agent_loop(user_task: str, messages: List[any], computer: PlaywrightComputer, MAX_STEPS = 10): 
    """Run the CUA loop"""
    # Capture Screenshot (first interaction)
    await asyncio.sleep(3)  # TODO(TO REMOVE)
    state: ComputerState = await computer.current_state()
    messages.append(
        {
            "role": "user",
            "content": [
                {'type': 'text', 'text': user_task}, 
                {'type': 'image_url', 'image_url': {
                    "url" : f"data:image/png;base64,{state.screenshot}"
                }}
            ]
        }
    )
    C_STEP=0 ## For loop counter
    while True: 
        # Loop couter logic 
        C_STEP+=1
        if C_STEP>MAX_STEPS: 
            print("Exceeded loop count limit")
            break

        # call model 
        step = create_response(messages)
        print("\n[MODEL OUTPUT]")
        print(step)

        # execute action 
        state = await execute_actions(step, computer)

        if state == "done": 
            print("[INFO] Task completed")
            break

        # Capture observation
        messages.append(
            {
                'role': 'user', 
                'content' : [
                    {'type': 'text', 'text': 'Observation after previous action'}, 
                    {'type': 'image_url', 'image_url': {
                        'url' : f"data:image/png;base64,{state.screenshot}"
                    }}
                ]
            }
        )
                    

async def main(): 
    user_task = input("Task > ")
    messages = []

    # Initialize playwright computer instance
    # Define user_data_dir path
    profile_name = 'browser_profile_for_cua'
    profile_path = os.path.join(tempfile.gettempdir(), profile_name)
    os.makedirs(profile_path, exist_ok=True)

    async with PlaywrightComputer(
        screen_size=(936, 684),
        user_data_dir=profile_path,
        highlight_mouse=True
    ) as computer:  
        width, height = await computer.screen_size()
        print(f"[INFO] Screen size: {width}x{height}")
        messages.append(
            {
                "role": "system",
                "content": OS_SYSTEM_PROMPT.format(screen_dimension = f"({width} x {height})")
            }
        )

        await cua_agent_loop(user_task=user_task, messages=messages,computer=computer)



if __name__ == "__main__": 
    asyncio.run(main())