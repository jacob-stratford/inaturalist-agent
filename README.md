# Nate - an Inaturalist Agent  

Nate is a llm-based agent that can answer questions about local wildlife sightings using the inaturalist API.


## Setup

You will need to obtain an api key for Google Gemini. You can get a limited-use one for free through your Google account at https://aistudio.google.com/apikey

Once you have your api key, export it to your environment variables
`export API_KEY=<your_api_key>`


After that, install dependencies
`pip install -r requirements.txt`


## Run Nate

Finally, run Nate with the command
`python nate.py`


## Prompt Examples

`Get observations for the sonoran horned lizard (200591) in Arizona (40) in 2024.`

`How many observations are there for each type of rattlesnake that has been observed in arizona? Arizona area code is 40. Plot the number of observations for each non-pigmy species, labeling with the species' common name`







