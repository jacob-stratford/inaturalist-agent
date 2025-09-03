
# Tools that the inaturalist agent can call

#from pyinaturalist import *
from pyinaturalist import get_taxa, get_observation_species_counts, TaxonCount
import requests
import pandas as pd
import pdb

from data_objects import DataFrame

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
    name = "GetTaxonID"
    declaration = {
        "name": name,
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
                    "description": "rank by which to filter results, default to species"
                }
            },
            "required": ["taxon_str"]
        }
    }

    @classmethod
    def call(cls, taxon_str, iconic_taxon_name=None, rank="species"):
        results = get_taxa(q=taxon_str, rank=rank)['results']
        results_abbreviated = cls.abbreviate_organism_search_results(results, iconic_taxon_name=iconic_taxon_name)
        return results_abbreviated, None

    @classmethod
    def abbreviate_organism_search_results(cls, results, iconic_taxon_name):
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



class GetLocationID(Tool):

    name = "GetLocationID"
    declaration = {
        "name": "GetLocationID",
        "description": "Search on a keyword to find related location names and their ID numbers. Returns a list of dictionaries containing key information about the locations returned by the search, including id, name, display_name, place_type, admin_level, location (lat,lon), and ancestor_place_ids (list of id-name pairs for location ancestors)",
        "parameters": {
            "type": "object",
            "properties": {
                "location_str": {
                    "type": "string",
                    "description": 'string to search, for example "Tucson" or "Pima County"'
                }
            },
            "required": ["location_str"]
        }
    }

    @classmethod
    def call(cls, location_str):
        url = "https://api.inaturalist.org/v1/places/autocomplete?q="
        url += location_str
        url += "&order_by=area"
        response = requests.get(url)
        res = response.json()
        
        results_abbreviated = cls.abbreviate_location_search_result(res['results'])
        return results_abbreviated, None

    @classmethod
    def abbreviate_location_search_result(cls, res):
        if not res:
            return {}
        results = []
        for res_ in res:
            location = {}
            location['id'] = res_['id']
            location['name'] = res_['name']
            location['display_name'] = res_['display_name']
            location['place_type'] = res_['place_type']
            location['admin_level'] = res_['admin_level']
            location['location'] = res_['location']
            location['ancestor_place_ids'] = cls.get_ancestor_names(res_['ancestor_place_ids'])
            results.append(location)
        return results
           
    @classmethod
    def get_ancestor_names(cls, ids):
        return None
        #if not ids:
        #    return None
        #return ids
        #for id in ids:
        #    pass 


class GetObservationData(Tool):

    name = "GetObservationData"
    declaration = {
        "name": "GetObservationData",
        "description": "Get location, time, and other observation data based on a taxonID, placeID pair",
        "parameters": {
            "type": "object",
            "properties": {
                "taxon_id": {
                    "type": "integer",
                    "description": 'taxon_id by which to filter observations'
                },
                "place_id": {
                    "type": "integer",
                    "description": 'place_id for the georaphic region that observations are pulled from'
                },
                "dataframe_name": {
                    "type": "string",
                    "description": "Name of DataFrame that stores result"
                }

            },
            "required": ["taxon_id", "place_id", "dataframe_name"]
        }
    }

    @classmethod
    def call(cls, taxon_id=None, place_id=None, dataframe_name=False):
        if taxon_id is None or place_id is None:
            return "Need a taxon_id or a place_id"
        results = get_observation_species_counts(place_id=place_id, taxon_id=taxon_id)

        if dataframe_name is None:
            results = str(results)[:300]  # DO NOT REMOVE otherwise the output is HUGE and will use up all my tokens!
            results = results[:250] + "\n\nPartial answer because this is still under development."
            print(results)
            return results
       
        results = results['results']
        data_dict = {
            'taxon_id': [res['taxon']['id'] for res in results],
            'rank': [res['taxon']['rank'] for res in results],
            'iconic_taxon_id': [res['taxon']['iconic_taxon_id'] for res in results],
            'name': [res['taxon']['name'] for res in results],
            'ancestry': [res['taxon']['ancestry'] for res in results],
            'extinct': [res['taxon']['extinct'] for res in results],
            'photo_url': [res['taxon']['default_photo']['url'] for res in results],
            'photo_attribution': [res['taxon']['default_photo']['attribution'] for res in results],
            'observations_count': [res['taxon']['observations_count'] for res in results],
            'wikipedia_url': [res['taxon']['wikipedia_url'] for res in results],
            'iconic_taxon_name': [res['taxon']['iconic_taxon_name'] for res in results],
            'conservaton_status': [res['taxon']['conservation_status']['status_name'] if 'conservation_status' in res['taxon'] else None for res in results],
            'preferred_common_name': [res['taxon']['preferred_common_name'] if 'preferred_common_name' in res['taxon'] else None for res in results]
        }

        df = pd.DataFrame(data_dict)
        if df is None:
            return "No DataFrame Produced", None
        DF = DataFrame(dataframe_name, df)
        return DF.get_summary(), DF


##taxa = TaxonCount.from_json_list(response['results'][:10])
#pprint(taxa)
#with open("data.json", "w") as json_file:
#    json.dump(response, json_file, indent=4)




