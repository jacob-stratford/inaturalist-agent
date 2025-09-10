
from google.genai import Client
from google.genai.types import Tool, GenerateContentConfig
import nate_tools
import json

# TODO: 
# - gracefully work when no tools are provided

class LLM:
    def __init__(self, api_key, model=None, tools=None):
        # api key to use the model
        # llm model, 
        # list of tool descriptions in gemini format
        self.client = Client(
            api_key=api_key,
        )
        self.model = model if model is not None else "gemini-2.0-flash"
        self.tools = tools if tools else [nate_tools.Tool.declaration]
        self.llm_tools = Tool(function_declarations=self.tools)
        self.config = GenerateContentConfig(
            tools=[self.llm_tools], 
        )

    def call(self, contents):
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=self.config
        )
        content = response.candidates[0].content
        usage = {
            "input_tokens": response.usage_metadata.prompt_token_count,
            "output_tokens": response.usage_metadata.candidates_token_count,
            "total_tokens": response.usage_metadata.total_token_count
        }
        return content, usage

    def count_tokens(self, contents):
        # returns int
        response = self.client.models.count_tokens(
            model=self.model,
            contents=contents
        )
        return response.total_tokens

def test():
    set_light_values_declaration = {
        "name": "set_light_values",
        "description": "Sets the brightness and color temperature of a light.",
        "parameters": {
            "type": "object",
            "properties": {
                "brightness": {
                    "type": "integer",
                    "description": "Light level from 0 to 100. Zero is off and 100 is full brightness",
                },
                "color_temp": {
                    "type": "string",
                    "enum": ["daylight", "cool", "warm"],
                    "description": "Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`.",
                },
            },
            "required": ["brightness", "color_temp"],
        },
    }
    with open("../API_KEY.txt", "r") as file:
        api_key = file.read().strip()
    #tools = [set_light_values_declaration]
    tools = []
    llm = LLM(api_key, tools=tools)
    prompt = "Do you have any available functions? Don't test them or call them in any way - just tell me yes or no and the names of any functions available" 
    num_input_tokens = llm.count_tokens(prompt)
    texts, function_calls, usage = llm.call(prompt)
    print("\ninput str: " + prompt)
    print("\ninput tokens: " + str(num_input_tokens))
    print("\nresponse: " + str(texts))
    print("\nfunction_call: " + str(function_calls))
    print("\nusage: " + str(usage))


#test()



