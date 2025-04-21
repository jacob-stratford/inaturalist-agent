
# Tools that the inaturalist agent can call

from pyinaturalist import *
import json

# Look up places near Tucson with the most Gila Monster observations
#response = get_places(q='Tucson', rank=['city', 'county'], per_page=5) # autocompleted. any good?
#response = get_observation_species_counts(place_id=6793, taxon_id=20979)

#taxa = TaxonCount.from_json_list(response['results'][:10])
#pprint(taxa)


#response = get_observation_identifiers(place_id=6793, taxon_id=20979)
#taxa = TaxonCount.from_json_list(response['results'][:10])
#pprint(taxa)


"""
       TOOLCALLs: [
           {
	       tool_name: "search_animalID",
	       "tool_args": {"animal_str": "coachwhip", "tax_levels": None},
	       "smart_output": {"animalID": int},
	       "smart_output_description": "Find the animalID that best fits the species ID for a coachwhip snake, also known as a red racer, which lives in the american southwest."
           },
           {
	       "tool_name": "search_locationID",
	       "tool_args": {"location_str": "Sabino Canyon', 'USstate': 'AZ'},
	       "smart_output": {"location(ID": int},
	       "smart_output_description": "Find the location ID that best fits Sabino Canyon, just north of Tucson, AZ"
           },
	   {
	       "tool_name": "get_sightings_data",
	       "tool_args": {"animalID": agent_objs['animalID'], "locationID": agent_objs['locationID']}
	       "smart_output": "coachwhip_sightings_in_sabino",
	       "smart_output_description": None
	   }
"""

def call_tool(tool_name, agent_objs, output_name, smart_output_instruction=None):
    # smart_output_instruction=None means that the whole output is saved to agent_objs
    str_to_tool(tool_name)
    pass

def str_to_tool(tool_name):
    if tool_name == "search_animalID":
        return search_animalID
    if tool_name == "search_locatioNID":
        return search_locatioNID
    if tool_name == "get_sightings":
        return get_sightings
    if tool_name == "make_histogram":
        return make_histogram
    if tool_name == "count_results":
        return count_results
    return None
   
def abbreviate_organism_search_results(results, iconic_taxon_name):
    abbreviated_fields = [
        'id',
        'rank',
        #'rank_level',
        #'iconic_taxon_id',
        #'ancestor_ids',
        #'is_active',
        'name',
        'extinct',
        'observations_count',
        #'wikipedia_url',
        'matched_term',
        'iconic_taxon_name',
        'preferred_common_name'
    ]
    results2 = []
    for result in results:
        if not result['is_active']:
            continue
        if result['iconic_taxon_name'] != iconic_taxon_name:
            continue
        abbreviated_result = {key: result[key] for key in abbreviated_fields if key in result}
        results2.append(abbreviated_result)
    return results2


def search_organismID(animal_str, rank=None, iconic_taxon_name=None):
    results = get_taxa(q=animal_str, rank=rank)['results']#, rank=['genus', 'family'])
    #print(type(results['results'][0]))
    #quit()
    results_abbreviated = abbreviate_organism_search_results(results, iconic_taxon_name=iconic_taxon_name)
    return results_abbreviated

def search_locatioNID(location_str, USstate=None, country=None):
    pass

def get_sightings(location_id = None, animal_id = None):
    pass

def make_histogram(data, bin_width=None):
    pass

def count_results(data):
    pass


animal = 'koala'
results = search_organismID(animal, rank=['species'], iconic_taxon_name="Mammalia")
with open('results.json', 'w') as f:
    json.dump(results, f, indent=4)






