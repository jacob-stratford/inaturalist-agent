
# Tools that the inaturalist agent can call

from pyinaturalist import *
import json

class Tool():
    def __init__(self):
        self.name = None
        self.required_args = {}
        self.optional_args = {}
        self.outputs = {}
        raise NotImplementedError

    def call(self, required_args, optional_args={}):
        raise NotImplementedError



class GetTaxonID(Tool):
    def __init__(self):
        self.name = "GetTaxonID"
        self.required_args = {
            "organism_str": 'string to search on, for example "bullfrog"'
        }
        self.optional_args = {
            "rank": 'list of ranks to search in. Defaults to all ranks. Acceptable ranks are ["kingdom", "phylum", "subphylum", "superclass", "subclass", "superorder", "order", "suborder", "infraorder", "superfamily", "epifamily", "family", "subfamily", "supertribe", "tribe", "subtribe", "genus", "genushybrid", "species", "hybrid", "subspecies", "variety", "form"]',
            "iconic_taxon_name": 'list of iconic taxononic groups to search in. Acceptble groups are ["Plantae", "Animalia", "Mollusca", "Reptilia", "Aves", "Amphibia", "Actinopterygii", "Mammalia", "Insecta", "Arachnida", "Fungi", "Protozoa", "Chromista", "unknow"]'
        }
        self.outputs = {
            "results": "list of dictionaries that describe the taxa that match the search parameters. Includes name, common name, rank, ID numer, number of observations, and extinction status"
        }

    def call(self, required_args={}, optional_args={}):
        missing_args = [arg for arg in self.required_args if arg not in required_args]
        if missing_args:
            raise Exception(tool.name + " is missing required args " + str(missing_args))

        rank = optional_args['rank'] if 'rank' in optional_args else None
        iconic_taxon_name = optional_args['iconic_taxon_name'] if 'iconic_taxon_name' in optional_args else None

        results = get_taxa(q=required_args['animal_str'], rank=rank)['results']
        results_abbreviated = abbreviate_organism_search_results(results, iconic_taxon_name=iconic_taxon_name)
        return results_abbreviated

    def abbreviate_organism_search_results(self, results, iconic_taxon_name):
        abbreviated_fields = [
            'id',
            'rank',
            #'rank_level',
            #'iconic_taxon_id',
            #'ancestor_ids',
            #'is_active',
            'name',
            #'extinct',
            'observations_count',
            #'wikipedia_url',
            'matched_term',
            'iconic_taxon_name',
            'preferred_common_name'
        ]
        abbreviated_results= []
        for result in results:
            if not result['is_active']:
                continue
            if (iconic_taxon_name is not None) and (result['iconic_taxon_name'] != iconic_taxon_name):
                continue
            if result['extinct']:
                continue
            abbreviated_result = {key: result[key] for key in abbreviated_fields if key in result}
            abbreviated_results.append(abbreviated_result)
        return abbreviated_results


def call_tool(tool_name, agent_objs, output_name, smart_output_instruction=None):
    # smart_output_instruction=None means that the whole output is saved to agent_objs
    str_to_tool(tool_name)
    pass

def str_to_tool(tool_name):
    if tool_name == "search_organismID":
        return search_organismID
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
        #'extinct',
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
        if (iconic_taxon_name is not None) and (result['iconic_taxon_name'] != iconic_taxon_name):
            continue
        if result['extinct']:
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


#animal = 'bullfrog'
#results = search_organismID(animal, rank=['species'], iconic_taxon_name="Mammalia")
#results = search_organismID(animal, rank=['species'])
#with open('results.json', 'w') as f:
#    json.dump(results, f, indent=4)






