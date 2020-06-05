# !/usr/bin/env python3

from pygtex import GeneModel, GenesModel, TissuesInfoModel, GTExAPIError
from pygtex import GeneExpressionModel, MedianGeneExpressionModel, TopExpressedGeneModel

# TissuesInfoModel
model = TissuesInfoModel()
print(','.join(model.getTissues('tissueSiteDetailAbbr')))


# GenesModel
gModel = GenesModel(['ace2'])
print("GeneSymbols:", ','.join(gModel.getGeneSymbols()))
print("GencodeIds:", ','.join(gModel.getGencodeIds()))
print("EntrezGeneIds:", ','.join(str(id) for id in gModel.getEntrezGeneIds()))


# GeneExpressionModel
geModel = GeneExpressionModel(
    gencodeIds=['ENSG00000186318.16'], 
    tissueSiteDetailIds=['Thyroid'], 
    # tissueSiteDetailIds=['Kidney_Medulla', 'Lung'], 
    sortBy="ageBracket"
    # sortBy="sex"
    )
# sort by tissue, subsetGroup, then median
expression = geModel.getGeneExpression()
expression.sort(key=lambda item: (item[0], item[3], item[1]))
for tissue, median, n, subsetGroup in expression:
    print("{:<40}Median={:.3f}TPM,\tn={},\tGroup={}".format(tissue, median, n, subsetGroup))


# MedianGeneExpressionModel
model = MedianGeneExpressionModel(
    gencodeIds=['ENSG00000182240.15', 'ENSG00000130234.10'],
    tissueSiteDetailIds=['Esophagus_Gastroesophageal_Junction', 'Esophagus_Mucosa', 'Esophagus_Muscularis'])

print(model.getGenesCluster())
print(model.getTissuesCluster())
print(model.getMedianExpression())


# TopExpressedGeneModel
tegModel = TopExpressedGeneModel('Esophagus_Gastroesophageal_Junction', 20)
print(tegModel.isTopExpressedGene(geneSymbol='MT-ND3'))
print(tegModel.isTopExpressedGene('ENSG00000130234.10'))
