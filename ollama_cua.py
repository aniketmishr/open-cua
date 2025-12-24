import ollama
from utils.function_parser import extract_function_calls_from_text, FunctionCall
from utils.prompts import OS_SYSTEM_PROMPT
from typing import List, Dict
from computers.local_playwright import LocalPlaywrightBrowser

def extract_action(model_output: str): 
    function_calls = extract_function_calls_from_text(model_output)
    print("Function call : ",function_calls[0])
    return function_calls[0]

def create_response(messages:List[Dict]): 
    response = ollama.chat(
        model='ahmadwaqar/smolvlm2-agentic-gui',  # or :fp16
        messages=messages
    )
    return response['message']['content']

def execute_action(action: FunctionCall, computer):
    """
    Execute a single parsed action on the computer.
    """
    action_type = action.function_name
    action_param = action.parameters

    if action_type == "click":
        computer.click(action_param["x"], action_param["y"])

    elif action_type == "double_click":
        computer.double_click(action_param["x"], action_param["y"])

    elif action_type == "type":
        computer.type(action_param["text"])

    elif action_type == "scroll":
        computer.scroll(
            action_param["x"],
            action_param["y"],
            action_param["scroll_x"], # TODO(Replace scroll_x with direction)
            action_param["scroll_y"]  # TODO(Replace scroll_y with amount)
        )

    elif action_type == "wait":
        computer.wait(int(action_param["seconds"]*1000))

    elif action_type == "final_answer":
        return action_param["answer"] if action_param else "done"

    else:
        raise ValueError(f"Unknown action: {action_type}")

    return "continue"

def main(): 
    """Run the CUA loop, using Local Playwright."""
    user_task = input("Task > ")
    with LocalPlaywrightBrowser() as computer:
        width, height = computer.get_dimensions()
        print(f"[INFO] Screen size: {width}x{height}")
        
        while True: 
            # Capture Screenshot
            screenshot_base64 = computer.screenshot()
            # build model input
            messages = [
                {
                    "role": "system",
                    "content": OS_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_task,
                    "images": [screenshot_base64]
                }
            ]
            # call model 
            raw_output = create_response(messages)
            print("\n[MODEL OUTPUT]")
            print(raw_output)

            try: 
                # extract action from raw output
                action = extract_action(raw_output)
            except ValueError as e: 
                print(f"[ERROR] {e}")
                break
             # execute action 
            result = execute_action(action, computer)

            if result != "continue": 
                if result == "done": 
                    print("[INFO] Task completed")
                    break
                else: 
                    print("[INFO] Task completed\n [MODEL OUTPUT]\n", result)
                    



if __name__ == "__main__": 
    main()