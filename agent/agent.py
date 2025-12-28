
import asyncio
import opik 
from agent.model import get_agent_next_step
from agent.schema import AgentStep, Click,Hover,DragAndDrop,Search,Type, Scroll, GoBack,Key,Navigate,Wait,Terminate
from agent.prompts import OS_SYSTEM_PROMPT
from computer.playwright import ComputerState
from computer.base_computer import BaseComputer
from dotenv import load_dotenv

load_dotenv()

opik.set_tracing_active(True)

class Agent:
    def __init__(self, computer: BaseComputer ,model: str = "openai/gpt-5-mini",system_prompt: str = ""):
        self.model = model 
        self.system = system_prompt
        self.computer = computer
        self.messages = []
        if self.system: 
            self.messages.append({"role": "system", "content": self.system})
    @opik.track
    async def _decide(self, message: str, state: ComputerState):
        self.messages.append(
            {
                "role": "user",
                "content": [
                    {'type': 'text', 'text': message}, 
                    {'type': 'image_url', 'image_url': {
                        "url" : f"data:image/png;base64,{state.screenshot}"
                    }}
                ]
            }
        )
        result = await get_agent_next_step(self.model, messages=self.messages)
        self.messages.append({"role": "assistant", "content" : str(result.model_dump_json())})  # Stores structred output in messages as assistant response
        return result
    
    async def _execute(self, step: AgentStep) -> ComputerState:
        action = step.action
        if isinstance(action, Click): 
            state = await self.computer.click_at(action.x, action.y)
        elif isinstance(action, Hover): 
            state = await self.computer.hover_at(action.x, action.y)
        elif isinstance(action, DragAndDrop): 
            state = await self.computer.drag_and_drop(action.x, action.y, action.destination_x, action.destination_y)
        elif isinstance(action, Search): 
            state = await self.computer.search(action.query, action.search_engine)
        elif isinstance(action, Type): 
            state = await self.computer.type_text_at(action.x, action.y, action.text, action.press_enter, action.clear_before_typing)
        elif isinstance(action, Scroll): 
            state = await self.computer.scroll_at(action.x, action.y, action.direction, action.magnitude)
        elif isinstance(action, GoBack): 
            state = await self.computer.go_back()
        elif isinstance(action, Key): 
            state = await self.computer.key_combination(action.keys)
        elif isinstance(action, Navigate): 
            state = await self.computer.navigate(action.url)
        elif isinstance(action, Wait): 
            state = await self.computer.wait(action.seconds)
        else: 
            raise ValueError("Invalid Action type")
        return state 
    @opik.track
    async def run(self, task: str, max_turns = 10):
        await self.computer.wait_for_load_state() 
        state: ComputerState = await self.computer.current_state()
        message = task
        c = 0
        while c<max_turns: 
            # Decide next agent step 
            step = await self._decide(message,state)
            print("\n[MODEL OUTPUT]")
            print(step)

            # Check if task is terminated
            if isinstance(step.action, Terminate): 
                print(f"[INFO] Task Status : {step.action.status}")
                if step.action.result: 
                    print(f"[INFO] Task Result : {step.action.result}") 
                return step.action

            # execute action 
            state = await self._execute(step)

            # observation
            message = "Observation: Action executed successfully. "

            # Increase the counter
            c+=1