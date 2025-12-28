import asyncio
import uuid
from agent.agent import Agent
import os, tempfile
from agent.prompts import OS_SYSTEM_PROMPT
from computer.playwright import PlaywrightComputer

DEFAULT_VISION_MODEL = "openai/gpt-5-mini"

async def run_cua_agent(task: str, model: str = DEFAULT_VISION_MODEL):
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
        thread_id = str(uuid.uuid4())
        agent = Agent(computer = computer, model = model, system_prompt=OS_SYSTEM_PROMPT.format(screen_dimension = f"({width} x {height})"))

        task_status = await agent.run(task = task, opik_args={"trace": {"thread_id": thread_id, "metadata": {"model": model, "computer_type" : computer.computer_env}}})
        return task_status


async def main(): 
    print("Open-CUA: Computer Using Agent 🤖")
    task = input("Task 💻 > ")
    model = input("Model 🧠 > ")

    await run_cua_agent(task, model if model.strip() else DEFAULT_VISION_MODEL)



if __name__ == "__main__": 
    asyncio.run(main())