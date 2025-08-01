
# Tools that the inaturalist agent can call

#from pyinaturalist import *
from pyinaturalist import get_taxa
import json
import requests

class Tool():

    declaration = {
        "name": "dummyFunction",
        "description": "Returns True",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }

    @classmethod
    def call(self, required_args, optional_args={}):
        raise NotImplementedError

    @classmethod
    def get_declaration(cls):
        return cls.declaration


class GetTaxonID(Tool):
    declaration = {
        "name": "GetTaxonID",
        "description": "Search on a keyword to find related taxon names and their ID numbers. Returns a list of dictionaries containing key information about the tasons returned by the search, including name, common name, rank, ID numer, and number of observations",
        "parameters": {
            "type": "object",
            "properties": {
                "taxon_str": {
                    "type": "string",
                    "description": 'String to search on, for example "bullfrog"',
                },
                "iconic_taxon_name": {
                    "type": "string",
                    "enum": ["Plantae", "Animalia", "Mollusca", "Reptilia", "Aves", "Amphibia", "Actinopterygii", "Mammalia", "Insecta", "Arachnida", "Fungi", "Protozoa", "Chromista", "unknow"],
                    "description": "Iconic taxononic group by which to filter results"
                },
                "rank": {
                    "type": "string",
                    "enum": ["kingdom", "phylum", "subphylum", "superclass", "subclass", "superorder", "order", "suborder", "infraorder", "superfamily", "epifamily", "family", "subfamily", "supertribe", "tribe", "subtribe", "genus", "genushybrid", "species", "hybrid", "subspecies", "variety", "form"],
                    "description": "rank by which to filter results"
                }
            },
            "required": ["taxon_str"]
        }
    }


    #@classmethod
    #def call(cls, required_args={}, optional_args={}):
    #    missing_args = [arg for arg in cls.required_args if arg not in required_args]
    #    if missing_args:
    #        raise Exception(tool.name + " is missing required args " + str(missing_args))

    #    rank = optional_args['rank'] if 'rank' in optional_args else None
    #    iconic_taxon_name = optional_args['iconic_taxon_name'] if 'iconic_taxon_name' in optional_args else None

    #    results = get_taxa(q=required_args['organism_str'], rank=rank)['results']
    #    results_abbreviated = cls.abbreviate_organism_search_results(cls, results, iconic_taxon_name=iconic_taxon_name)
    #    return results_abbreviated

    #def abbreviate_organism_search_results(self, results, iconic_taxon_name):
    #    abbreviated_fields = [
    #        'id',
    #        'rank',
    #        #'rank_level',
    #        #'iconic_taxon_id',
    #        #'ancestor_ids',
    #        #'is_active',
    #        'name',
    #        #'extinct',
    #        'observations_count',
    #        #'wikipedia_url',
    #        'matched_term',
    #        'iconic_taxon_name',
    #        'preferred_common_name'
    #    ]
    #    abbreviated_results= []
    #    for result in results:
    #        if not result['is_active']:
    #            continue
    #        if (iconic_taxon_name is not None) and (result['iconic_taxon_name'] != iconic_taxon_name):
    #            continue
    #        if result['extinct']:
    #            continue
    #        abbreviated_result = {key: result[key] for key in abbreviated_fields if key in result}
    #        abbreviated_results.append(abbreviated_result)
    #    return abbreviated_results



class GetLocationID(Tool):

    declaration = {
        "name": "GetLocationID",
        "description": "Search on a keyword to find related location names and their ID numbers. Returns a list of dictionaries containing key information about the locations returned by the search, including id, name, display_name, place_type, admin_level, location (lat,lon), and ancestor_place_ids (list of id-name pairs for location ancestors)",
        "parameters": {
            "type": "object",
            "properties": {
                "location_str": {
                    "type": "string",
                    "description": 'string to search, for example "Tucson"'
                }
            },
            "required": ["location_str"]
        }
    }


    #@classmethod
    #def call(cls, required_args={}, optional_args={}):

    #    missing_args = [arg for arg in cls.required_args if arg not in required_args]
    #    if missing_args:
    #        raise Exception(tool.name + " is missing required args " + str(missing_args))

    #    url = "https://api.inaturalist.org/v1/places/autocomplete?q="
    #    url += required_args['location_str']
    #    url += "&order_by=area"
    #    response = requests.get(url)
    #    res = response.json()

    #    results_abbreviated = cls.abbreviate_location_search_result(res['results'])
    #    return results_abbreviated


    #@classmethod
    #def abbreviate_location_search_result(cls, res):
    #    if not res:
    #        return {}
    #    results = []
    #    for res_ in res:
    #        location = {}
    #        location['id'] = res_['id']
    #        location['name'] = res_['name']
    #        location['display_name'] = res_['display_name']
    #        location['place_type'] = res_['place_type']
    #        location['admin_level'] = res_['admin_level']
    #        location['location'] = res_['location']
    #        location['ancestor_place_ids'] = cls.get_ancestor_names(res_['ancestor_place_ids'])
    #        results.append(location)
    #    return results
           
    #@classmethod
    #def get_ancestor_names(cls, ids):
    #    if not ids:
    #        return None
    #    return ids
    #    for id in ids:
    #        pass 





# Look up places near Tucson with the most Gila Monster observations
#response = get_places(q='Tucson', rank=['city', 'county'], per_page=5) # autocompleted. any good?
#response = get_observation_species_counts(place_id=6793, taxon_id=20979)

#taxa = TaxonCount.from_json_list(response['results'][:10])
#pprint(taxa)


#response = get_observation_identifiers(place_id=6793, taxon_id=20979)
#taxa = TaxonCount.from_json_list(response['results'][:10])
#pprint(taxa)

# Find locations with "Tucson" in the name:
#response = GetLocationID.call(required_args={"location_str": "Tucson"})
#print("response:")
#for res in response:
#    print(res['name'], res['ancestor_place_ids'])



