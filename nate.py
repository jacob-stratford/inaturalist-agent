
from google.genai import types
import json
from llm import LLM
import argparse
import os

from nate_tools import GetTaxonID, GetLocationID, GetObservationData, GetObservations, ReadDF

# This is the code for actually running the agent


def parse_args():
    parser = argparse.ArgumentParser(description="A simple script demonstrating store_true.")
    #parser.add_argument('', type=str, help='a string')
    parser.add_argument('--test', action='store_true', help='Load test datasets at init')
    return parser.parse_args()


class Nate:
    def __init__(self, api_key, system_prompt_path, tools=None, objs=None):
        self.api_key = api_key
        self.chat_hist = []
        self.objs = {}
        system_prompt = self.load_system_prompt(system_prompt_path)
        assert objs is None or type(objs) == dict, "objs must be None or dict"
        if objs is not None:
            system_prompt += "\n\nYou have access to the following data objects:\n"
            for obj_name in objs:
                system_prompt += objs[obj_name].get_summary() + "\n"
                self.objs[obj_name] = objs[obj_name]
        else:
            self.objs = {}

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

                function_response_part = types.Part.from_function_response(
                    name=part.function_call.name,
                    response={"result": tool_result},
                )
                self.chat_hist.append(types.Content(role="user", parts=[function_response_part])) # tool repsponse
        if call_again:
            self.call()

    def print_message(self, role, message):
        print("\n" + role + ":\n" + message + "\n")
        
    def call_tool(self, function_call):
        tool_result, obj = self.tools_dict[function_call.name].call(self.objs, **function_call.args)
        if obj is not None:
            self.objs[obj.name] = obj.data
        return tool_result

    def get_user_input(self):
        print("\nUSER:")
        user_input = input()
        self.add_msg("user", user_input)
        if user_input[:4] == "quit" or user_input[:4] == "exit" or user_input == "q":
            print('quitting...')
            quit()

    
def main(args):

    api_key = os.getenv("API_KEY")
    fname = "prompt.txt"
    tools = [GetTaxonID, GetLocationID, GetObservationData, GetObservations, ReadDF]
    objs = None

    if args.test:
        import pandas as pd
        from data_objects import DataFrame
        df_fname = "test.csv"
        obj_raw = pd.read_csv(df_fname)
        obj = DataFrame("test_df", obj_raw)
        objs={obj.name: obj}
    nate = Nate(api_key, fname, tools=tools, objs=objs)

    print("\nNATE:")
    print("Hello, I'm an assistant for helping you find answers to your ecological questions. What would you like me to do?")

    while True:
        nate.get_user_input()
        nate.call()


if __name__ == "__main__":
    main(parse_args())


