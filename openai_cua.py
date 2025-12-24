from openai import OpenAI
from utils.function_parser import extract_function_calls_from_text, FunctionCall
from utils.prompts import OS_SYSTEM_PROMPT
from typing import List, Dict, Literal, Union
from pydantic import BaseModel, Field
from computers.local_playwright import LocalPlaywrightBrowser

from dotenv import load_dotenv

load_dotenv()
MODEL = "gpt-5-mini"

# Structured Output
class ClickAction(BaseModel): 
    type : Literal["click"]
    x: float = Field(..., ge=0.0,le=1.0,description="Normalized X (0-1)")
    y: float = Field(..., ge=0.0,le=1.0,description="Normalized Y (0-1)")

class TypeAction(BaseModel): 
    type: Literal["type"]
    text : str = Field(..., description="Text to type")

class ScrollAction(BaseModel): 
    type : Literal["scroll"]
    dx: int = 0
    dy: int = Field(..., description="vertical scroll amount")

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

def execute_actions(agent_output: CUAOutput, computer):
    """
    Execute a single parsed action on the computer.
    """
    for action in agent_output.actions: 
        screen_width, screen_height = computer.get_dimensions() 

        if action.type== "click":
            # scale click parameters
            computer.click(action.x*screen_width, action.y*screen_height)

        # elif action_type == "double_click":
        #     computer.double_click(action_param["x"]*screen_width, action_param["y"]*screen_height)

        elif action.type == "type":
            computer.type(action.text)

        elif action.type == "scroll":
            computer.scroll(
                action.dx, 
                action.dy, 
                action.dx, 
                action.dy       # Computer Scroll takes diff. input format TODO('fix paramenter mismatch')
            )

        elif action.type == "wait":
            computer.wait(int(action.seconds*1000))

        elif action.type == "done":
            return "done"

        else:
            raise ValueError(f"Unknown action: {action}")

    return "continue"

def main(): 
    """Run the CUA loop"""
    user_task = input("Task > ")
    messages = []
    with LocalPlaywrightBrowser() as computer:
        width, height = computer.get_dimensions()
        print(f"[INFO] Screen size: {width}x{height}")
        messages.append(
            {
                "role": "system",
                "content": OS_SYSTEM_PROMPT.format(screen_dimension = f"({width} x {height})")
            }
        )
        # Capture Screenshot (first interaction)
        screenshot_base64 = computer.screenshot()
        messages.append(
            {
                "role": "user",
                "content": [
                    {'type': 'text', 'text': user_task}, 
                    {'type': 'image_url', 'image_url': {
                        "url" : f"data:image/png;base64,{screenshot_base64}"
                    }}
                ]
            }
        )
        c=0 ## For loop counter
        while True: 
            # Loop couter logic 
            c+=1
            if c>6: 
                print("Exceeded loop count limit")
                break

            # call model 
            step = create_response(messages)
            print("\n[MODEL OUTPUT]")
            print(step)

            # execute action 
            result = execute_actions(step, computer)

            if result == "done": 
                print("[INFO] Task completed")
                break

            # Capture observation
            obs_screenshot_base64 = computer.screenshot()
            messages.append(
                {
                    'role': 'user', 
                    'content' : [
                        {'type': 'text', 'text': 'Observation after previous action'}, 
                        {'type': 'image_url', 'image_url': {
                            'url' : f"data:image/png;base64,{obs_screenshot_base64}"
                        }}
                    ]
                }
            )
                    



if __name__ == "__main__": 
    main()