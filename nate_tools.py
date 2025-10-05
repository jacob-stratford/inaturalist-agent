
# Tools that the inaturalist agent can call

#from pyinaturalist import *
from pyinaturalist import get_taxa, get_observation_species_counts, TaxonCount
import requests
import pandas as pd
import pdb
import re
from datetime import datetime
import math
import plotly.express as px
import plotly.graph_objects as go

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
    def call(self, objs):
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
    def call(cls, objs, taxon_str, iconic_taxon_name=None, rank="species"):
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
    def call(cls, objs, location_str):
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


class GetObservationSummary(Tool):

    name = "GetObservationSummary"
    declaration = {
        "name": "GetObservationSummary",
        "description": "Get name, common name, rank, extinction status, observation count, and wikipedia link for all observations that are descended from taxonID and are within a placeID (one row per species)",
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
    def call(cls, objs, taxon_id=None, place_id=None, dataframe_name=False):
        if taxon_id is None or place_id is None:
            return "Need a taxon_id or a place_id", None
        results = get_observation_species_counts(place_id=place_id, taxon_id=taxon_id)

        if dataframe_name is None:
            results = str(results)[:300]  # DO NOT REMOVE otherwise the output is HUGE and will use up all my tokens!
            results = results[:250] + "\n\nPartial answer because this is still under development."
            print(results)
            return results, None
       
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


class GetObservations(Tool):

    name = "GetObservations"
    declaration = {
        "name": "GetObservations",
        "description": "Get a dataframe of many individual observations including location, time, and other observation data based on a taxonID, placeID pair and other params",
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
                },
                "d1": {
                    "type": "string",
                    "description": "Earliest datetime for observations, formatted YYYY-MM-DD"
                },
                "d2": {
                    "type": "string",
                    "description": "Latest datetime cutoff for observations, formatted YYYY-MM-DD"
                },
                "n": {
                    "type": "integer",
                    "description": "Max number of observations to return, default is unlimited"
                }
                # Consider replacing d1, d2, etc. with an open "params" input object/string

            },
            "required": ["taxon_id", "place_id", "dataframe_name"]
        }
    }

    @classmethod
    def call(cls, objs, taxon_id=None, place_id=None, dataframe_name=False, d1=None, d2=None, n=None):

        # Parameter validation
        if taxon_id is None or place_id is None:
            return "Error: taxon_id and place_id are required", None

        api_url = 'https://api.inaturalist.org/v1/observations'
        params = {
            'taxon_id': taxon_id,
            'place_id': place_id,
            'per_page': 100  # Will be adjusted per page as needed
        }
        if d1 is not None:
            params['d1'] = d1
        if d2 is not None:
            params['d2'] = d2

        all_results = []
        page = 1

        while True:
            # Adjust per_page for final page when n is specified
            remaining = n - len(all_results) if n else params['per_page']
            params['per_page'] = min(100, max(1, remaining)) if remaining > 0 else params['per_page']

            print(f"Fetching page {page}...")
            params['page'] = page

            try:
                response = requests.get(api_url, params=params, timeout=30)
                if response.status_code != 200:
                    return f"Error: API request failed with status {response.status_code}", None

                data = response.json()
            except requests.exceptions.RequestException as e:
                return f"Error: Request failed - {str(e)}", None
            except ValueError as e:
                return f"Error: Failed to parse JSON response - {str(e)}", None

            observations = data.get("results", [])

            if not observations:
                break

            all_results.extend(observations)

            # Check if we've reached the limit
            if n and len(all_results) >= n:
                all_results = all_results[:n]
                break

            # Check if this was the last page (fewer results than requested per_page)
            if len(observations) < params['per_page']:
                break

            page += 1
    
        parsed_data = []
        for obs in all_results:
            # Safely extract nested data with a fallback
            taxon = obs.get('taxon', {})
            user = obs.get('user', {})
            photos = obs.get('photos', [])
            default_photo = photos[0] if photos else {}
    
            # Construct attribution string
            attribution = ""
            if 'id' in obs and user.get('login'):
                attribution = f"Photo by {user['login']} via iNaturalist. View the observation: https://www.inaturalist.org/observations/{obs['id']}"
    
            parsed_data.append({
                'observation_id': obs.get('id'),
                'verifiable': obs.get('verifiable'),
                'quality_grade': obs.get('quality_grade'),
                'observed_on': obs.get('observed_on'),
                'created_at': obs.get('created_at'),
                'latitude': obs.get('latitude'),
                'longitude': obs.get('longitude'),
                'scientific_name': taxon.get('name'),
                'common_name': taxon.get('preferred_common_name'),
                'taxon_id': taxon.get('id'),
                'user_id': user.get('id'),
                'user_login': user.get('login'),
                'place_ids': obs.get('place_ids'),
                'wikipedia_url': taxon.get('wikipedia_url'),
                'default_photo_url': default_photo.get('url'),
                'default_photo_attribution': default_photo.get('attribution'),
                'all_photo_urls': [photo.get('url') for photo in photos],
                'attribution': attribution
            })
    
        df = pd.DataFrame(parsed_data)
        
        # Convert dates to datetime objects for better handling
        df['observed_on'] = pd.to_datetime(df['observed_on'], errors='coerce')
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')

       
        # Make and return the Nate DataFrame 
        if df is None:
            return "No DataFrame Produced", None
        DF = DataFrame(dataframe_name, df)
        return DF.get_summary(), DF
        #return str(df)[:500], None


# TODO:
# - update the output format to include a text summary, plus a Nate dataframe with the correct name
# - Consider updating to allow other parameters as inputs
# - reduce the space used for attributions, and generate on the fly as necessary
# - Test thouroughly
# - Add a separate tool for making histograms


class ReadDF(Tool):

    name = "ReadDF"
    declaration = {
    "name": "ReadDF",
    "description": "Read a DataFrame object, specifying columns, number of rows, and filters.",
    "parameters": {
        "type": "object",
        "properties": {
            "df": {
                "type": "string",
                "description": 'DataFrame object name'
            },
            "cols": {
                "type": "array",
                "description": 'List of column names to include in the result. Defaults to all.',
                "items": {
                    "type": "string"
                }
            },
            "n": {
                "type": "integer",
                "description": "Max number of rows to read. Default 5, max 20."
            },
            "query_tuples": {
                "type": "array",
                "description": "List of len=3 tuples for querying the dataframe, where each tuple has the format (column, op, val). The following operations are allowed: {\"=\", \">\", \"<\", \">=\", \"<=\", \"!=\"}. The value 'val' will be a string and is casted to the correct type by the function.",
                "items": {
                    "type": "array",
                    "minItems": 3,
                    "maxItems": 3,
                    "items": {
                        "type": "string"
                    }
                }
            },
            "sort_by": { 
                "type": "array",
                "description": 'List of (column name, asc/desc) tuples to sort by. Specify ascending or descending for each, as in [("column_name", "desc")].',
                "items": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        },
        "required": ["df"]
    }
    }

    @classmethod
    def call(cls, objs, df=None, cols=None, n=5, query_tuples=None, sort_by=None):
        if df is None:
            raise ValueError("Need a dataframe name")

        if df not in objs:
            raise ValueError(f"DataFrame '{df}' not found")

        if type(cols) != list and cols is not None:
            raise ValueError("cols must be a list")

        if n < 1:
            raise ValueError("n must be greater than 0")

        if n > 20:
            raise ValueError("n must be less than or equal to 20")

        ALLOWED_OPS = {"=", "==", ">", "<", ">=", "<=", "!="}
        SAFE_COL_RE = re.compile(r'^[A-Za-z0-9_ ]+$')

        def safe_filter(df_obj, column, op, value):
            if op not in ALLOWED_OPS:
                raise ValueError("Operation not allowed")
            elif op == "=":
                op = "=="
            if column not in df_obj.columns:
                raise ValueError("Column not found")
            if not SAFE_COL_RE.match(column):
                raise ValueError(f"Unsafe column name: {column}")

            # Determine the target data type from the DataFrame's dtypes
            target_dtype = df_obj.dtypes[column]
            casted_value = None
        
            try:
                # Check if the column is a datetime type
                if pd.api.types.is_datetime64_any_dtype(target_dtype):
                    casted_value = pd.to_datetime(value)
                # Check if the column is a numeric type (int, float)
                elif pd.api.types.is_numeric_dtype(target_dtype):
                    casted_value = pd.to_numeric(value)
                # Check for boolean types
                elif pd.api.types.is_bool_dtype(target_dtype):
                    if value.lower() in ['true', '1', 't', 'y', 'yes']:
                        casted_value = True
                    elif value.lower() in ['false', '0', 'f', 'n', 'no']:
                        casted_value = False
                    else:
                        raise ValueError(f"Cannot convert '{value}' to boolean.")
                # If none of the above, assume it's a string and use the original value
                else:
                    casted_value = value

            except (ValueError, TypeError) as e:
                raise ValueError(f"Could not cast value '{value}' to type '{target_dtype}': {e}")

            return f"`{column}` {op} @casted_value", casted_value


        df_filt = objs[df].data.copy()
        cols_filt = df_filt.columns if cols is None else cols

        missing = set(cols_filt) - set(df_filt.columns)
        if missing:
            raise ValueError(f"Columns not found: {missing}")

        if query_tuples is not None:
            if type(query_tuples) != list:
                raise ValueError("query_tuples must be a list")
            for qt in query_tuples:
                expr, casted_value = safe_filter(df_filt, qt[0], qt[1], qt[2])
                df_filt = df_filt.query(expr, local_dict={"casted_value": casted_value})

        # --- Sorting Logic ---
        if sort_by is not None:
            if not isinstance(sort_by, list):
                raise ValueError("sort_by must be a list of columns or (column, 'desc') tuples.")

            sort_cols = []
            sort_ascending = []

            for item in sort_by:
                col_name = None
                ascending = True

                if isinstance(item, str):
                    col_name = item
                elif isinstance(item, list) and len(item) == 2 and item[1].lower() in ('asc', 'desc'):
                    col_name = item[0]
                    if item[1].lower() == 'desc':
                        ascending = False
                else:
                    raise ValueError(f"Invalid sort item: {item}. Must be 'column_name' or ['column_name', 'desc'/'asc'].")

                if col_name not in df_filt.columns:
                    raise ValueError(f"Sort column '{col_name}' not found in DataFrame.")

                sort_cols.append(col_name)
                sort_ascending.append(ascending)

            # Apply sorting
            df_filt = df_filt.sort_values(by=sort_cols, ascending=sort_ascending)

        # --- End Sorting Logic ---

        return str(df_filt[cols_filt].head(n)), None


class PlotHistogram(Tool):

    name = "PlotHistogram"
    declaration = {
        "name": name,
        "description": "Plot a histogram of a numeric column from a DataFrame using plotly and display it in the browser.",
        "parameters": {
            "type": "object",
            "properties": {
                "df": {
                    "type": "string",
                    "description": 'DataFrame object name'
                },
                "column": {
                    "type": "string",
                    "description": 'Column name to plot the histogram for (must be numeric)'
                },
                "nbins": {
                    "type": "integer",
                    "description": "Number of bins for the histogram, defaults to 50"
                },
                "bin_size": {
                    "type": "number",
                    "description": "Size of bins for the histogram (overrides nbins if provided)"
                }
            },
            "required": ["df", "column"]
        }
    }

    @classmethod
    def call(cls, objs, df=None, column=None, nbins=50, bin_size=None):
        if df is None:
            return "Error: df parameter is required", None
        if column is None:
            return "Error: column parameter is required", None

        if df not in objs:
            return f"Error: DataFrame '{df}' not found", None

        pandas_df = objs[df].data
        if column not in pandas_df.columns:
            return f"Error: Column '{column}' not found in DataFrame '{df}'", None

        if not pd.api.types.is_numeric_dtype(pandas_df[column]):
            return f"Error: Column '{column}' is not numeric", None

        try:
            if bin_size is not None:
                fig = go.Figure(data=[go.Histogram(x=pandas_df[column], xbins=dict(size=bin_size))])
            else:
                fig = px.histogram(pandas_df, x=column)
            fig.show()
            return f"Histogram for column '{column}' in DataFrame '{df}' has been plotted and opened in the browser.", None
        except Exception as e:
            return f"Error creating histogram: {str(e)}", None


##taxa = TaxonCount.from_json_list(response['results'][:10])
#pprint(taxa)
#with open("data.json", "w") as json_file:
#    json.dump(response, json_file, indent=4)
