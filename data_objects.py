
import pandas as pd

class DataObject:
    def __init__(self, name, data):
        self.name = name
        self.data = data


class DataFrame(DataObject):
    def __init__(self, name, data):
        assert type(name) == str
        assert isinstance(data, pd.DataFrame)
        super().__init__(name, data)

    def get_summary(self):
        """ Returns a string with a summary of the dataframe """
        output = (f"{self.name} is a pandas DataFrame with {len(self.data)} rows " +
                "and the following columns: " +
                str([col for col in self.data.columns])) 
        return output


