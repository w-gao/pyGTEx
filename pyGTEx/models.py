import json
import logging
from typing import Optional, Dict, Any

import requests
from abc import ABC, abstractmethod

from pyGTEx.errors import GTExAPIError


class Model(ABC):
    """
    An abstract class that encapsulates data retrieved from a GTEx API call into
    Python objects.
    """
    # to be concatenated in later classes to get to desired endpoints
    baseUrl = "https://gtexportal.org/rest/v1/"

    def __init__(self, path: str):
        self.path = path
        self.data = None  # raw data fetched from the API

    @abstractmethod
    def _fetch(self):
        """
        Sub-classes should override this method to populate `self.data` with its
        respective data structures.

        This method is intended to be called only once during instantiation.
        """
        raise NotImplementedError

    def _getJsonFromUrl(self, params: Optional[Dict[str, Any]] = None):
        """
        Returns the contents of the URL parsed as JSON.

        :raise GTExAPIError: If failed to fetch from server or parse response
                             into JSON.
        """
        try:
            response = requests.get(self.baseUrl + self.path, params=params)
            if not response.ok:
                raise RuntimeError("Failed to fetch data from URL.")
            return json.loads(response.content)
        except Exception as ex:
            # either failed to fetch data or failed to parse json
            raise GTExAPIError("Failed to fetch from API: " + str(ex)) from ex


class TissuesInfoModel(Model):
    """
    Represents the dataset retrieved from the `dataset/tissueInfo` endpoint.
    """
    # Sample response:
    # {
    #     tissueInfo: [
    #         {
    #             datasetId: "gtex_v8",
    #             samplingSite: "Subcutaneous tissue beneath the leg's skin sample.",
    #             tissueSite: "Adipose Tissue",
    #             tissueSiteDetail: "Adipose - Subcutaneous",
    #             tissueSiteDetailAbbr: "ADPSBQ",
    #             tissueSiteDetailId: "Adipose_Subcutaneous",
    #             uberonId: "0002190"
    #         }, ...
    # }

    def __init__(self,
                 tissueSite: Optional[str] = None,
                 tissueSiteDetailAbbr: Optional[str] = None,
                 tissueSiteDetailId: Optional[str] = None):
        super().__init__("dataset/tissueInfo")
        self.tissueSite = tissueSite
        self.tissueSiteDetailAbbr = tissueSiteDetailAbbr
        self.tissueSiteDetailId = tissueSiteDetailId
        self._fetch()

    def _fetch(self):
        if self.data: return

        results = self._getJsonFromUrl(params={
            "tissueSite": self.tissueSite,
            "tissueSiteDetailAbbr": self.tissueSiteDetailAbbr,
            "tissueSiteDetailId": self.tissueSiteDetailId,
        })
        if 'tissueInfo' not in results:
            raise GTExAPIError('Invalid data from API: ', results)

        # populating self.data with the value of the tissueInfo data type from the results dictionary
        # this value is a list of dictionaries and each dictionary is a different type of tissue
        self.data = results['tissueInfo']

    def getTissues(self, form: str):
        """
        Get a list of tissues in the given form.

        :param form: One of 'tissueSite', 'tissueSiteDetail', 'tissueSiteDetailAbbr', or 'tissueSiteDetailId'.
        """
        return [tissue.get(form) for tissue in self.data]

