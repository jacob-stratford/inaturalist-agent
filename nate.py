
from google import genai
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
        self.tools = tools
        if tools is None:
            self.tools = []
            self.tools.append(GetTaxonID.get_declaration())
            self.tools.append(GetLocationID.get_declaration())
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
        response, function_call, usage = self.llm.call(self.chat_hist)
        self.print_message("NATE", response)
        self.add_msg('model', response)
        self.call_tools(function_call)

    def print_message(self, role, message):
        print("\n" + role + ":\n" + message + "\n")
        
    def call_tools(self, function_call):
        print('TOOLS CALLS')
        print(function_call)
        #toolcalls = self.extract_toolcalls(response)
        #if toolcalls is None:
        #    return
        #for toolcall in toolcalls:
        #    tool_response = str(self.call_tool(toolcall))
        #    self.add_msg("tool", tool_response)
        pass

    def extract_toolcalls(self, response):
        #marker = "TOOLCALLS:"
        #index = response.find(marker)
        #if index == -1:
        #    return None  # Marker not found
        #raw_json = response[index + len(marker):].strip()
        #return json.loads(raw_json)
        pass

    def call_tool(self, toolcall):
        #tool = str_to_tool(toolcall['tool_name'])
        #tool_response = tool(required_tool_args=tool['required_tool_args'], optional_tool_args=tool['optional_tool_args'])
        #return tool_response
        pass

    def get_user_input(self):
        print("\nUSER:")
        user_input = input()
        self.add_msg("user", user_input)
        if user_input[:4] == "quit" or user_input[:4] == "exit" or user_input == "q":
            print('quitting...')
            quit()


def test_nate():
    api_key = ""
    with open("../API_KEY.txt", "r") as file:
        api_key = file.read().strip()
    fname = "prompt.txt"
    nate = Nate(api_key, fname)

    print("\nNATE:")
    print("Hello, I'm an assistant for helping you find answers to your ecological questions. What would you like me to do?")
    
    user_input = "Do you have access to any functions? List any function names but don't call them"
    nate.add_msg("user", user_input)
    nate.print_message("user", user_input)
    nate.call()

    
def main():
   
    # DEBUG
    #test_nate()
    #quit()
    # END DEBUG

    api_key = ""
    with open("../API_KEY.txt", "r") as file:
        api_key = file.read().strip()
    fname = "prompt.txt"
    nate = Nate(api_key, fname)

    print("\nNATE:")
    print("Hello, I'm an assistant for helping you find answers to your ecological questions. What would you like me to do?")

    while True:
        nate.get_user_input()
        nate.call()


if __name__ == "__main__":
    main()



