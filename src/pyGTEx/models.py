import json
import logging
from typing import Optional, Dict, Any, List

import requests
from abc import ABC, abstractmethod

from pyGTEx.errors import GTExAPIError


class Model(ABC):
    """
    An abstract class that encapsulates data retrieved from a GTEx API call into
    Python objects.
    """
    # See docs: https://www.gtexportal.org/home/api-docs
    baseUrl = "https://gtexportal.org/rest/v1/"

    def __init__(self, path: str, gencodeVersion: str = "v26", genomeBuild: str = "GRCh38/hg38"):
        """
        :param path: The path to the full API endpoint of this model
        :param gencodeVersion: The gencode version to use for the queries. Must
                               be either be "v26" or "v19".
        :param genomeBuild: The genome build to use for the queries. Must be
                            either "GRCh38/hg38" or "GRCh37/hg19".
        """
        if not (gencodeVersion == "v26" and genomeBuild == "GRCh38/hg38" or
                gencodeVersion == "v19" and genomeBuild == "GRCh37/hg19"):
            raise ValueError("Mismatched GENCODE and genome build versions: ", gencodeVersion, genomeBuild)

        self.path = path
        self.gencodeVersion = gencodeVersion
        self.genomeBuild = genomeBuild

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
            params = {
                "gencodeVersion": self.gencodeVersion,
                "genomeBuild": self.genomeBuild,
                **params
            }
            logging.warning(params)
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
                 tissueSiteDetailId: Optional[str] = None,
                 *args, **kwargs):
        super().__init__("dataset/tissueInfo", *args, **kwargs)
        self.tissueSite = tissueSite
        self.tissueSiteDetailAbbr = tissueSiteDetailAbbr
        self.tissueSiteDetailId = tissueSiteDetailId
        self._fetch()

    def _fetch(self):
        if self.data:
            return

        results = self._getJsonFromUrl(params={
            "tissueSite": self.tissueSite,
            "tissueSiteDetailAbbr": self.tissueSiteDetailAbbr,
            "tissueSiteDetailId": self.tissueSiteDetailId,
        })
        if 'tissueInfo' not in results:
            raise GTExAPIError('Invalid data from API: ', results)

        self.data = results.get("tissueInfo")

    def getTissues(self, form: str):
        """
        Get a list of tissues in the given form.

        :param form: One of 'tissueSite', 'tissueSiteDetail', 'tissueSiteDetailAbbr', or 'tissueSiteDetailId'.
        """
        return [tissue.get(form) for tissue in self.data]


class GeneModel(Model):
    """
    Represents the dataset of a SINGLE gene retrieved from the `reference/gene`
    endpoint. Data returned from methods is only for protein coding genes.
    """
    # Sample response:
    # {
    #   "gene":[{
    #     "entrezGeneId":1636,
    #     "gencodeId":"ENSG00000159640.15",
    #     "geneSymbol":"ACE",
    #     "geneType":"protein coding",
    #     ...
    #    }, ...]
    # }

    def __init__(self, geneId: str, *args, **kwargs) -> None:
        """
        :param geneId: Either a gene symbol, versioned GENCODE (Ensembl) ID, or
                       un-versioned GENCODE ID. If an unambiguous geneId is
                       given, the first match from the GTEx query will be
                       returned.
        """
        super().__init__(path="reference/gene", *args, **kwargs)
        self.geneId = geneId
        self._fetch()

    def getGencodeId(self) -> str:
        """
        Convert input geneId to GENCODE ID.
        """
        return self.data.get("gencodeId")

    def getGeneSymbol(self) -> str:
        """
        Convert input geneId to gene Symbol.
        """
        return self.data.get("geneSymbol")

    def getEntrezGeneId(self) -> int:
        """
        Convert input geneId to Entrez gene ID.
        """
        return self.data.get("entrezGeneId")

    def getDescription(self) -> str:
        """
        Return the description of the gene.
        """
        return self.data.get("description")

    def _fetch(self) -> None:
        if self.data:
            return

        # "?format=json&geneId=" + geneId
        results = self._getJsonFromUrl(params={
            "format": "json",
            "geneId": self.geneId
        })

        if "gene" not in results:
            raise GTExAPIError("Invalid data from API: ", results)

        # should only be one iteration since only one gene is queried
        for gene in results.get("gene"):
            # skip non protein coding
            if gene.get("geneType") != "protein coding":
                continue

            if self.geneId.startswith("ENS"):
                # gencode Id provided; should be unique
                self.data = gene
                break
            elif gene.get("geneSymbol").lower() == self.geneId.lower():
                # gene symbol uniquely match
                self.data = gene
                break  # there might be more, but we only return the first match


class GenesModel(Model):
    """
    Represent the dataset of MULTIPLE genes retrieved from the `reference/gene`
    endpoint. Data returned from methods is only from protein coding genes.

    Note: Consider looking into GeneModel if you only need to retrieve a single
    gene from a unique gene ID.
    """
    # Sample response:
    # {
    #     "gene": [{
    #         "entrezGeneId":1636,
    #         "gencodeId":"ENSG00000159640.15",
    #         "geneSymbol":"ACE",
    #         "geneType":"protein coding",
    #         ...
    #     }, ...], ...
    # }

    def __init__(self, geneIds: List[str], *args, **kwargs):
        """
        :param geneIds: A list of gene symbol, versioned GENCODE (Ensembl) ID,
                        or un-versioned GENCODE ID.
        """
        super().__init__(path="reference/gene", *args, **kwargs)
        self.geneIds = geneIds
        self._fetch()

    def getGencodeIds(self) -> List[str]:
        """
        Convert input geneIds to GENCODE IDs while preserving the input order.
        """
        return [
            gene.get("gencodeId")
            for gene in self.data if gene.get("geneType") == "protein coding"
        ]

    def getGeneSymbols(self) -> List[str]:
        """
        Convert input geneIds to gene symbols while preserving the input order.
        """
        return [
            gene.get("geneSymbol")
            for gene in self.data if gene.get("geneType") == "protein coding"
        ]

    def getEntrezGeneIds(self) -> List[int]:
        """
        Convert input geneIds to Entrez gene IDs while preserving the input order.
        """
        return [
            gene.get("entrezGeneId")
            for gene in self.data if gene.get("geneType") == "protein coding"
        ]

    def _fetch(self) -> None:
        if self.data:
            return

        # "?format=json&geneId=" + ','.join(geneIds)
        results = self._getJsonFromUrl(params={
            "format": "json",
            "geneId": ",".join(self.geneIds)
        })

        if "gene" not in results:
            raise GTExAPIError("Invalid data from API: ", results)

        self.data = results.get("gene")

