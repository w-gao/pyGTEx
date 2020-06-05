# !/usr/bin/env python3

import urllib.request as urllib
import json
import ssl
import numpy as np

ssl._create_default_https_context = ssl._create_unverified_context  # create an SSL certificate to use HTTPS


class Model:
    """
    Represent a data structure encapsulated into its own object that allows interaction with data retreived from an API call.
    class attributes: baseUrl
    instance attributes: self.data, self._fetch(url)
    """
    # to be concatenated in later classes to get to desired endpoints
    baseUrl = "https://gtexportal.org/rest/v1/"

    def __init__(self, url):
        """
        Initializes self.data
        calls self._fetch with url parameter to populate self.data for use in later methods
        url - string, required
        """
        self.data = None  # raw data fetched from the API
        self._fetch(url)  # calls fetch method to populate self.data for each subclass

    def _fetch(self, url):
        """
        Sub-classes should override this method to populate `self.data` with its respective data stuctures.
        This method is intented to be called only once during instantiation.
        """
        # placeholder for subclasses to override.
        pass

    def _getJsonFromUrl(self, url):
        """
        Return response returned from the input url parsed into python containers, synchronously.
        A GTExAPIError is thrown when the URL is invalid or response is not in json form.
        """
        try:
            # an attempt to read the json formatted data from endpoint url
            return json.loads(
                urllib.urlopen(self.baseUrl + url).read()
            )
        except Exception as ex:
            # either failed to fetch data or failed to parse json
            raise GTExAPIError("Failed to fetch from API: " + str(ex)) from ex


class GTExAPIError(Exception):
    """ Error occurred when accessing or parsing data from the GTEx API."""
    pass


class TissuesInfoModel(Model):
    """
    Represent the dataset retrieved from the `dataset/tissueInfo` endpoint.
    methods: getTissues(), _fetch()
      {
      tissueInfo: [
       {
        datasetId: "gtex_v8",
        samplingSite: "Subcutaneous tissue beneath the leg's skin sample.",
        tissueSite: "Adipose Tissue",
        tissueSiteDetail: "Adipose - Subcutaneous",
        tissueSiteDetailAbbr: "ADPSBQ",
        tissueSiteDetailId: "Adipose_Subcutaneous",
        uberonId: "0002190"
       }, ...
      }
    """

    def __init__(self):
        """
        Calls on self._fetch(url) to retrieve data from api
        """
        super().__init__(url="dataset/tissueInfo")

    def getTissues(self, form):
        """
        Get a list of tissues in the given form.
        form - string, required : 'tissueSite', 'tissueSiteDetail', 'tissueSiteDetailAbbr', or 'tissueSiteDetailId'
        """
        return [tissue[form] for tissue in self.data]

    def _fetch(self, url):
        """ Overridden method from parent to fetch data from the `dataset/tissueInfo` endpoint."""
        # breaks out of code if self.data is already set
        # (this is the case for all _fetch methods)
        if self.data:
            return
        # saves the dataset in the format of a dictionary with data types as keys and the data as values
        results = self._getJsonFromUrl(url)
        if 'tissueInfo' not in results:
            raise GTExAPIError('Invalid data from API: ', results)
        # populating self.data with the value of the tissueInfo data type from the results dictionary
        # this value is a list of dictionaries and each dictionary is a different type of tissue
        self.data = results['tissueInfo']


class GeneModel(Model):
    """
    Represent the dataset of a SINGLE gene retrieved from the `reference/gene` endpoint.
    Data returned from methods is only for protein coding genes.
    methods: getGencodeId(), getGeneSymbol(), getEntrezGeneId(), _fetch()
      {"gene":[
       {
        "entrezGeneId":1636,
        "gencodeId":"ENSG00000159640.15",
        "geneSymbol":"ACE",
        "geneType":"protein coding",
        ...
       },
      ]
     """

    def __init__(self, geneId):
        """
        geneId - string, required : A gene symbol, versioned gencodeId, or unversioned gencodeId.
        """
        self.geneId = geneId
        super().__init__(url="reference/gene?format=json&geneId=" + geneId)

    def getGencodeId(self):
        """ Convert input to Genecode ID."""
        return self.data['gencodeId']

    def getGeneSymbol(self):
        """ Convert input to Gene Symbol."""
        return self.data['geneSymbol']

    def getEntrezGeneId(self):
        """ Convert input to EntrezGene ID."""
        return self.data['entrezGeneId']

    def _fetch(self, url):
        """ Overridden method from parent to fetch data from the `reference/gene` endpoint."""
        if self.data:
            return
        results = self._getJsonFromUrl(url)  # saves the dataset in the format of a dictionary
        if 'gene' not in results:
            raise GTExAPIError('Invalid data from API: ', results)

        # should only be one iteration since only one gene is queried
        for gene in results['gene']:
            if gene['geneType'] != 'protein coding':  # skip non protein coding
                continue  # does not execute following expressions if condition is met
            if self.geneId.startswith('ENS'):  # gencode Id provided; should be unique
                self.data = gene  # saves the gene information dictionary and breaks out of loop
                break
            elif gene['geneSymbol'].lower() == self.geneId.lower():  # gene symbol uniquely match
                self.data = gene
                break  # there might be more, but we break


class GenesModel(Model):
    """
    Represent the dataset retrieved from the `reference/gene` endpoint.
    Data returned from methods is only from protein coding genes.
    methods: getGencodeIds(), getGeneSymbols(), getEntrezGeneIds(), _fetch()
      {"gene":[
       {
        "entrezGeneId":1636,
        "gencodeId":"ENSG00000159640.15",
        "geneSymbol":"ACE",
        "geneType":"protein coding",
        ...
      }, ...
      ], ...}
    """

    def __init__(self, geneIds):
        """
        geneIds - list, required : A list of gene symbol, versioned gencodeId, or unversioned gencodeId
        """
        self.geneIds = geneIds
        super().__init__(url="reference/gene?format=json&geneId=" + ','.join(geneIds))

    def getGencodeIds(self):
        """
        Convert input to Genecode IDs.
        Returns Genecode IDs in list format.
        """
        return [gene['gencodeId'] for gene in self.data if gene['geneType'] == 'protein coding']

    def getGeneSymbols(self):
        """
        Convert input to Gene Symbols.
        Returns Gene Symbols in list format.
        """
        return [gene['geneSymbol'] for gene in self.data if gene['geneType'] == 'protein coding']

    def getEntrezGeneIds(self):
        """
        Convert input to EntrezGene IDs.
        Returns EntrezGene IDs in list format.
        """
        return [gene['entrezGeneId'] for gene in self.data if gene['geneType'] == 'protein coding']

    def _fetch(self, url):
        """ Overridden method from parent to fetch data from the `reference/gene` endpoint."""
        if self.data:
            return
        results = self._getJsonFromUrl(url)  # saves the dataset in the format of a dictionary
        if 'gene' not in results:
            raise GTExAPIError('Invalid data from API: ', results)
        # populating self.data with the value of the gene data type from the results dictionary
        # this value is a list of dictionaries and each dictionary is a different type of gene
        self.data = results['gene']


class GeneExpressionModel(Model):
    """
    Represent the dataset retrieved from the `expression/geneExpression` endpoint.
    Methods: getGeneExpression(), _fetch()
      {
        "geneExpression":[{
          "data":[22.97,22.1,15.52, ...],
          "datasetId":"gtex_v8",
          "gencodeId":"ENSG00000186318.16",
          "geneSymbol":"BACE1",
          "tissueSiteDetailId":"Thyroid",
          "unit":"TPM"
        }, ...
      ]}
    """

    def __init__(self, gencodeIds, tissueSiteDetailIds=None, sortBy=None):
        """
        gencodeIds: list, required : A list of versioned GENCODE ID of a gene, e.g. ['ENSG00000065613.9.', '...']
        tissueSiteDetailId: list, optional : A list of tissue ID of the tissue of interest.
        sortBy: string, optional : 'sex' or 'ageBracket'
        """
        url = "expression/geneExpression?datasetId=gtex_v8&format=json&gencodeId=" + ','.join(gencodeIds)
        # checks if this list exists and concatenates tissues to url for API query
        if tissueSiteDetailIds:
            url += "&tissueSiteDetailId=" + ','.join(tissueSiteDetailIds)
        # checks if this string exists and concatenates it to url for API query
        if sortBy:
            url += "&attributeSubset=" + sortBy
        super().__init__(url)

    def getGeneExpression(self):
        """ Return a list of tuples with format [(tissueSiteDetailId, median, n, subsetGroup), ...]."""
        return [(tissue['tissueSiteDetailId'],
                 # uses numpy to calculate the median since only full dataset is given
                 np.median(tissue['data'] or [0]),  # 0 median if data is empty
                 len(tissue['data']),
                 tissue.get('subsetGroup', None))  # store subsets as well for sorting
                for tissue in self.data]

    def _fetch(self, url):
        """ Overridden method from parent to fetch data from the `expression/geneExpression` endpoint."""
        if self.data:
            return
        results = self._getJsonFromUrl(url)  # saves dictionary of all data retrieved from API query
        if 'geneExpression' not in results:
            raise GTExAPIError('Invalid data from API: ', results)
        # populating self.data with the value of the geneExpression data type from the results dictionary
        # this value is a list of dictionaries and each dictionary is a different type of gene
        self.data = results['geneExpression']


class MedianGeneExpressionModel(Model):
    """
    Represent the dataset retrieved from the `expression/medianGeneExpression` endpoint.
    methods: getMedianExpression(), getGeneCluster(), getTissueCluster(), _fetch()
      {
      clusters: {
        gene: "**Newick format**",
        tissue: "**Newick format**"
      },
      medianGeneExpression: [
       {
        datasetId: "gtex_v8",
        gencodeId: "ENSG00000130234.10",
        geneSymbol: "ACE2",
        median: 0.774831,
        tissueSiteDetailId: "Esophagus_Gastroesophageal_Junction",
        unit: "TPM"
       }, ...
      ]}
    """

    def __init__(self, gencodeIds, tissueSiteDetailIds):
        """
        gencodeIds - list, required : A list of versioned GENCODE ID of a gene, e.g. ['ENSG00000065613.9.', '...']
        tissueSiteDetailIds - list, required : A list of tissue ID of the tissue of interest.
        """
        self.clusters = None  # clusters could be None

        url = "expression/medianGeneExpression?hcluster=true&pageSize=10000&gencodeId={}&tissueSiteDetailId={}" \
            .format(','.join(gencodeIds), ','.join(tissueSiteDetailIds))
        super().__init__(url)

    def getGenesCluster(self):
        """ Return a cluster based on genes in Newick format."""
        # condition handles the case where there is not enough genes queried for cluster information to be generated
        if not self.clusters or self.clusters['gene'].startswith('Not enough data'):
            return None
        return self.clusters['gene']

    def getTissuesCluster(self):
        """ Return a cluster based on tissues in Newick format."""
        # condition handles the case where there is not enough tissues queried for cluster information to be generated
        if not self.clusters or self.clusters['tissue'].startswith('Not enough data'):
            return None
        return self.clusters['tissue']

    def getMedianExpression(self):
        """
        Return two containers: ordered genes and medians in a dictionary of lists: [Gene1, Gene2], {"Tissue1": [1,2], ...}.
        """
        genes = []
        medians = {}

        for entry in self.data:
            # appends gene symbols to genes list
            if entry['geneSymbol'] not in genes:
                genes.append(entry['geneSymbol'])

            # From lecture 14
            try:  # attempts to add median to an existing entry list
                medians[entry['tissueSiteDetailId']].append(entry['median'])
            except KeyError:  # if there is no such list then a new key, value pair is created
                medians[entry['tissueSiteDetailId']] = [entry['median']]

        return genes, medians

    def _fetch(self, url):
        """ Overridden method from parent to fetch data from the `expression/medianGeneExpression` endpoint."""
        if self.data:
            return
        # saves the dataset in the format of a dictionary with data types as keys and the data as values
        results = self._getJsonFromUrl(url)
        if 'medianGeneExpression' not in results:
            raise GTExAPIError('Invalid data from API: ', results)
        # populating self.data with the value of the medianGeneExpression data type from the results dictionary
        # this value is a list of dictionaries and each dictionary is a different type of gene with associated tissue
        self.data = results['medianGeneExpression']
        # populating self.clusters with the value of cluster data type from the results dictionary
        # this value is a dictionary with information on the cluster data for either genes or tissues
        if 'clusters' in results:
            self.clusters = results['clusters']


class TopExpressedGeneModel(Model):
    """
    Represent the dataset retrieved from the `expression/topExpressedGene` endpoint.
    methods: isTopExpressedGene(), getTopGenesInfo()
      {
        ...,
        "topExpressedGene": [
          {
            "datasetId": "gtex_v8",
            "gencodeId": "ENSG00000198886.2",
            "geneSymbol": "MT-ND4",
            "median": 20948.5,
            "tissueSiteDetailId": "Ovary",
            "unit": "TPM"
          }, ...
      }
    """

    def __init__(self, tissueSiteDetailId, num=100):
        """
        tissueSiteDetailId - string, required : A tissue ID of the tissue of interest.
        num - integer, optional : A number of genes that will be fetched from the top expressed list.
        """
        url = "expression/topExpressedGene?datasetId=gtex_v8&tissueSiteDetailId={}&sortBy=median&sortDirection=desc&pageSize={}" \
            .format(tissueSiteDetailId, num)
        super().__init__(url)

    def isTopExpressedGene(self, geneSymbol, gencodeId=None):
        """ Return a boolean denoting the given gencodeId is or is not top expressed in the tissue of interest."""
        for gene in self.data:  # checks for a matching gene identifier in each gene information dictionary
            # gencodeId is prioritized if given.
            if gencodeId:
                if gene['gencodeId'] == gencodeId:
                    return gene['median']  # the median of the gene is returned if found
            else:
                if gene['geneSymbol'] == geneSymbol:
                    return gene['median']
        return False  # if nothing is returned in iteration then False is returned

    def getTopGenesInfo(self):
        """ Return a list of dictionary with gene symbols as keys and their median expression as the value. """
        topExDict = {}
        # iterates through all gene information dictionaries and creates new key value pairs for topExDict
        for geneDict in self.data:
            topExDict[geneDict["geneSymbol"]] = geneDict["median"]

        return topExDict

    def _fetch(self, url):
        """ Overridden method from parent to fetch data from the `expression/topExpressedGene` endpoint."""
        if self.data:
            return
        # saves the dataset in the format of a dictionary with data types as keys and the data as values
        results = self._getJsonFromUrl(url)
        if 'topExpressedGene' not in results:
            raise GTExAPIError('Invalid data from API: ', results)
        # populating self.data with the value of the topExpressedGene data type from the results dictionary
        # this value is a list of dictionaries and each dictionary is a different type of gene
        self.data = results['topExpressedGene']


def getSimilarExpression(gencodeGenes, tissues):
    """
    Returns a dictionary with queried tissues as keys and lists of sets of similarly expressed genes as values.
    Similarly expressed genes are relative to those queried and three or more genes are required for input.
    gencodeGenes - list, required: Gencode IDs for genes desired
    tissues - lists within a list, required: valid tissue IDs for tissues desired each tissue has to be its own list
    """
    similarExpressionDict = {}
    # creates objects for tissues separately to obtain more accurate clusters
    for tissue in tissues:
        # obtaining the clusters
        medianGeneObj = MedianGeneExpressionModel(gencodeGenes, tissue)
        rawNewickFormat = medianGeneObj.getGenesCluster()
        # creating a new entry for the similarExpressionDict
        similarExpressionDict[tissue[0]] = []
        # splitting the given cluster string into identifiable genes
        for item1 in rawNewickFormat.split("("):
            firstList = item1.split(")")
            for item2 in firstList:
                secondList = item2.split(",")
                finalListSet = set()  # set will represent clustered genes
                # in the final list all the items clustered together will be in the same list as a proper gene
                for item3 in secondList:
                    finalList = item3.split(":")
                    for gene in finalList:
                        # translating the genecode ID to the gene symbol while filtering out invalid strings
                        if gene in gencodeGenes:
                            geneObj = GeneModel(gene)
                            geneSymbol = geneObj.getGeneSymbol()
                            finalListSet.add(geneSymbol)
                if finalListSet:  # clustered genes are appended to list of relative clusters within a tissue
                    similarExpressionDict[tissue[0]].append(finalListSet)
    return similarExpressionDict
