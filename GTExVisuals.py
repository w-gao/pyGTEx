#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import seaborn
from Bio import Phylo
from io import StringIO
from pygtex import GeneModel, GenesModel, TissuesInfoModel, GTExAPIError
from pygtex import GeneExpressionModel, MedianGeneExpressionModel, TopExpressedGeneModel


class GTExVisualError(Exception):
    """ Error related to visualization when using pandas, matplotlib, or seaborn."""
    pass


def parseRawTissues(tissues):
    """
    Return a list of `tissueSiteDetailId`s that can be recognized by the API.
    tissues - a list of integers containing tissue indices.
    """
    tModel = TissuesInfoModel()
    return [tModel.getTissues('tissueSiteDetailId')[int(id)] for id in tissues]


# GeneExpression

def plotGeneExpression(gene, tissueIds, sortBy="ageBracket", kind="bar", title='Gene Expression by Median', figsize=None, rot=None, xlabel='Tissues', ylabel='Median (TPM)'):
    """
    gene - a string of gene symbols, versioned gencode Ids, or unversioned gencode Ids.
    tissueIds - a list of tissueSiteDetailIds.
    sortBy - can be 'ageBracket' or 'sex'
    kind - the kind of plot to produce (bar, barh, etc)
    title, figsize, rot, xlabel, ylabel - settings for matplotlib
    """
    gencodeId = GeneModel(gene).getGencodeId()

    if not gencodeId or not len(tissueIds):
        raise GTExVisualError('Invalid input gene or tissues.')

    geModel = GeneExpressionModel([gencodeId], tissueIds, sortBy)
    expression = geModel.getGeneExpression()

    # sort by tissue, subsetGroup, then median
    expression.sort(key=lambda item: (item[0], item[3], item[1]))

    # further parse our data
    tissues = []
    data = {}

    for tissue, median, n, subsetGroup in expression:
        if tissue not in tissues:
            tissues.append(tissue)
        try:
            data[subsetGroup].append(median)
        except KeyError:
            data[subsetGroup] = [median]

    # convert to pandas DataFrame
    df = pd.DataFrame(data=data, index=tissues)

    graph = df.plot(kind=kind, title=title, figsize=figsize, rot=rot)
    graph.set(xlabel=xlabel, ylabel=ylabel)


# MedianGeneExpression

def _getMedianGeneExpressionModel(genes, tissueIds):
    """
    Internal function for MedianGeneExpression related visualization.
    Return a MedianGeneExpressionModel object containing the median gene expression data of the given genes and tissues.
    """
    gencodeIds = GenesModel(genes).getGencodeIds()

    if not len(gencodeIds) or not len(tissueIds):
        raise GTExVisualError('Invalid input gene or tissues.')

    return MedianGeneExpressionModel(gencodeIds, tissueIds)


def plotMedianGeneExpression(genes, tissueIds, kind="bar", title='Median Gene Expression', figsize=None, rot=None, xlabel='Gene', ylabel='Median (TPM)'):
    """
    genes - a list of gene symbols, versioned gencode Ids, or unversioned gencode Ids.
    tissueIds - a list of tissueSiteDetailIds.
    kind - the kind of plot to produce (bar, barh, etc)
    title, figsize, rot, xlabel, ylabel - settings for matplotlib
    """
    mModel = _getMedianGeneExpressionModel(genes, tissueIds)
    index, data = mModel.getMedianExpression()
    df = pd.DataFrame(data=data, index=index)
    # df = df.transpose()

    # https://pandas.pydata.org/pandas-docs/stable/user_guide/visualization.html
    plt = df.plot(kind=kind, title=title, figsize=figsize, rot=rot)
    plt.set(xlabel=xlabel, ylabel=ylabel)


def plotMedianGeneExpressionClusters(genes, tissueIds, clusteredBy="tissues"):
    """
    genes - a list of gene symbols, versioned gencode Ids, or unversioned gencode Ids.
    tissueIds - a list of tissueSiteDetailIds.
    clusteredBy - can be 'tissues' or 'genes'
    """
    mModel = _getMedianGeneExpressionModel(genes, tissueIds)
    if clusteredBy == "genes":
        clusters = mModel.getGenesCluster()
    elif clusteredBy == "tissues":
        clusters = mModel.getTissuesCluster()
    else:
        raise GTExVisualError('Invalid cluster: {}'.format(clusteredBy))

    if not clusters:
        raise GTExAPIError('Cluster data is not available by {}.'.format(clusteredBy))

    tree = Phylo.read(StringIO(clusters), "newick")
    # Phylo.draw_ascii(tree)
    Phylo.draw(tree, axes=plt.axes(frame_on=False, xticks=[], yticks=[]))


def plotMedianGeneExpressionHeatmap(genes, tissueIds):
    """
    genes - a list of gene symbols, versioned gencode Ids, or unversioned gencode Ids.
    tissueIds - a list of tissueSiteDetailIds.
    """
    mModel = _getMedianGeneExpressionModel(genes, tissueIds)
    index, data = mModel.getMedianExpression()
    df = pd.DataFrame(data=data, index=index)
    seaborn.heatmap(df, cmap='YlGnBu', linewidths=0.5, robust=True, annot=True)


# TopExpressedGene
def plotTopExpressedGene(tissueId, num=50, kind="bar", title=None, figsize=None, rot=None, xlabel='Genes', ylabel='Median (TPM)'):
    """
    tissueIds - a list of tissueSiteDetailIds.
    kind - the kind of plot to produce (bar, barh, etc)
    title, figsize, rot, xlabel, ylabel - settings for matplotlib
    """
    title = title or 'Top Genes Expressed in {} by Median'.format(tissueId)
    teModel = TopExpressedGeneModel(tissueId, num)
    topExGenes = teModel.getTopGenesInfo()  # dictionary of top expressed genes with their median expression values
    # sort the dictionary in descending order
    sortedGenes = {gene: median for gene, median in sorted(topExGenes.items(), key=lambda item: item[1], reverse=True)}
    df = pd.DataFrame(data=sortedGenes.values(), index=sortedGenes.keys())
    graph = df.plot(kind=kind, title=title, figsize=figsize, rot=rot, legend=False)
    graph.set(xlabel=xlabel, ylabel=ylabel)
