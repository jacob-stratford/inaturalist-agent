
from google import genai
from google.genai import types
import json
from nate_tools import GetTaxonID, GetLocationID
from llm import LLM

# This is the code for actually running the agent

class Nate:
    def __init__(self, api_key, system_prompt_path, tools=None):
        self.api_key = api_key
        self.chat_hist = []
        system_prompt = self.load_system_prompt(system_prompt_path)
        self.add_msg('user', system_prompt)
        self.add_msg('model', 'I understand the instructions, and I will act accordingly')
        self.tools = [] if tools else None
        self.tools_dict = {}
        if tools is not None:
            for tool in tools:
                self.tools.append(tool.get_declaration())
                self.tools_dict[tool.name] = tool

        self.llm = LLM(self.api_key, tools=self.tools)
        
    def load_system_prompt(self, fname):
        sys_prompt = ""
        with open(fname, 'r') as f:
            sys_prompt += f.read()
        return sys_prompt
        
    def add_msg(self, role, content):
        msg = {'role': role, 'parts': [{'text': content}]}
        self.chat_hist.append(msg)
       
    def call(self):
        content, usage = self.llm.call(self.chat_hist)
        self.chat_hist.append(content) # Model's Tool Call
        call_again = False
        for part in content.parts:
            if part.text is not None:
                self.print_message("NATE", part.text)
            elif part.function_call is not None:
                call_again = True
                self.print_message("TOOL", part.function_call.name + str(part.function_call.args))
                tool_result = self.call_tool(part.function_call)

                function_response_part = genai.types.Part.from_function_response(
                    name=part.function_call.name,
                    response={"result": tool_result},
                )
                self.chat_hist.append(types.Content(role="user", parts=[function_response_part])) # tool repsponse
        if call_again:
            self.call()

    def print_message(self, role, message):
        print("\n" + role + ":\n" + message + "\n")
        
    def call_tool(self, function_call):
        tool_result = self.tools_dict[function_call.name].call(**function_call.args)
        return tool_result

    def get_user_input(self):
        print("\nUSER:")
        user_input = input()
        self.add_msg("user", user_input)
        if user_input[:4] == "quit" or user_input[:4] == "exit" or user_input == "q":
            print('quitting...')
            quit()

    
def main():
   
    api_key = ""
    with open("../API_KEY.txt", "r") as file:
        api_key = file.read().strip()
    fname = "prompt.txt"
    tools = [GetTaxonID, GetLocationID]
    nate = Nate(api_key, fname, tools=tools)

    print("\nNATE:")
    print("Hello, I'm an assistant for helping you find answers to your ecological questions. What would you like me to do?")

    while True:
        nate.get_user_input()
        nate.call()


if __name__ == "__main__":
    main()


