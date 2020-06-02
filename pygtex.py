# -----------------------------------------------------------------
# pygtex.py
# -----------------------------------------------------------------

#!/usr/bin/env python3

import urllib
import json
import ssl
ssl._create_default_https_context = ssl._create_unverified_context # create an SSL certificate to use HTTPS
import numpy as np

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
    self._fetch(url)

  def _fetch(self):
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
          urllib.request.urlopen(self.baseUrl + url).read()
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
    Subclass of Model class 
    inherits attribute: self.data 
    Calls on self._fetch(url)
    Defines endpoint url dataset/tissueInfo
    """
    super().__init__(url="dataset/tissueInfo")
  
  def getTissues(self, form):
    """
    Get a list of tissues in the given form.
    form - string, required : 'tissueSite', 'tissueSiteDetail', 'tissueSiteDetailAbbr', or 'tissueSiteDetailId'
    """
    # goes through tissue keys in self.data and returns the tissue name depending on the form the user specifies 
    return [tissue[form] for tissue in self.data]

  def _fetch(self, url):
    """ Overridden method from parent to fetch data from the `dataset/tissueInfo` endpoint."""
    if self.data: # breaks out of code if self.data is already set
      return
    results = self._getJsonFromUrl(url) # returns the dataset in the format of a dictionary
    if 'tissueInfo' not in results: 
      raise GTExAPIError('Invalid data from API: ', results)
    self.data = results['tissueInfo'] # populating self.data with the tissueInfo section of the results dictionary


class GenesModel(Model):
  """
  Represent the dataset retrieved from the `reference/gene` endpoint.
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
    geneIds - list, required : A list of gene symbol, versioned gencodeId, or unversioned gencodeId.
    """
    super().__init__(url="reference/gene?format=json&geneId=" + ','.join(geneIds))

  def getGencodeIds(self):
    """ Convert input to Genecode IDs."""
    return [gene['gencodeId'] for gene in self.data if gene['geneType'] == 'protein coding']  

  def getGeneSymbols(self):
    """ Convert input to Gene Symbols."""
    return [gene['geneSymbol'] for gene in self.data if gene['geneType'] == 'protein coding']

  def getEntrezGeneIds(self):
    """ Convert input to EntrezGene IDs."""
    return [gene['entrezGeneId'] for gene in self.data if gene['geneType'] == 'protein coding']

  def _fetch(self, url):
    """ Overridden method from parent to fetch data from the `reference/gene` endpoint."""
    if self.data: # breaks out of code if self.data is already set
      return
    results = self._getJsonFromUrl(url) # returns the dataset in the format of a dictionary
    if 'gene' not in results:
      raise GTExAPIError('Invalid data from API: ', results)
    # populating self.data with the gene section of the results dictionary
    self.data = results['gene'] 


class GeneExpressionModel(Model):
  """
  Represent the dataset retrieved from the `expression/geneExpression` endpoint.
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
    if tissueSiteDetailIds:
      url += "&tissueSiteDetailId=" + ','.join(tissueSiteDetailIds)
    if sortBy:
      url += "&attributeSubset=" + sortBy
    super().__init__(url)

  def getGeneExpression(self):
    """ Return a list of tuples with format [(tissueSiteDetailId, median, n, subsetGroup), ...]."""
    return [(tissue['tissueSiteDetailId'], 
             np.median(len(tissue['data'])), 
             len(tissue['data']), 
             tissue.get('subsetGroup', None)) # This is where age sorting is implemented 
      for tissue in self.data if len(tissue['data'])] # only return entries that contain data points. 
    
  def _fetch(self, url):
    """ Overridden method from parent to fetch data from the `expression/geneExpression` endpoint."""
    if self.data:
      return
    results = self._getJsonFromUrl(url)
    if 'geneExpression' not in results:
      raise GTExAPIError('Invalid data from API: ', results)
    self.data = results['geneExpression']



class MedianGeneExpressionModel(Model):
  """
  Represent the dataset retrieved from the `expression/medianGeneExpression` endpoint.
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
    self.clusters = None # clusters could be None

    url = "expression/medianGeneExpression?hcluster=true&pageSize=10000&gencodeId={}&tissueSiteDetailId={}" \
      .format(','.join(gencodeIds), ','.join(tissueSiteDetailIds))
    super().__init__(url)

  def getGenesCluster(self):
    """ Return a cluster based on genes in Newick format."""
    if not self.clusters or self.clusters['gene'].startswith('Not enough data'):
      return None
    return self.clusters['gene']

  def getTissuesCluster(self):
    """ Return a cluster based on tissues in Newick format."""
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
      if entry['geneSymbol'] not in genes:
        genes.append(entry['geneSymbol'])
        
      # From lecture 14
      try:
        medians[entry['tissueSiteDetailId']].append( entry['median'] )
      except KeyError:
        medians[entry['tissueSiteDetailId']] = [ entry['median'] ]

    return genes, medians

  def _fetch(self, url):
    """ Overridden method from parent to fetch data from the `expression/medianGeneExpression` endpoint."""
    if self.data:
      return
    results = self._getJsonFromUrl(url)
    if 'medianGeneExpression' not in results:
      raise GTExAPIError('Invalid data from API: ', results)
    
    self.data = results['medianGeneExpression']
    if 'clusters' in results:
      self.clusters = results['clusters']


class TopExpressedGeneModel(Model):
  """
  Represent the dataset retrieved from the `expression/topExpressedGene` endpoint.
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
    for gene in self.data:
      # gencodeId is prioritized if given.
      if gencodeId:
        if gene['gencodeId'] == gencodeId:
          return gene['median']
      else:
        if gene['geneSymbol'] == geneSymbol:
          return gene['median']
    return False
  
  def _fetch(self, url):
    """ Overridden method from parent to fetch data from the `expression/topExpressedGene` endpoint."""
    if self.data:
      return
    results = self._getJsonFromUrl(url)
    if 'topExpressedGene' not in results:
      raise GTExAPIError('Invalid data from API: ', results)
    self.data = results['topExpressedGene']
