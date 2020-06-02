"""# Example 1"""

# output datapoints of median gene expression
import pandas as pd

def main():
  # fake user input
  genes = ['ACTN3', 'SLK', 'ENSG00000121879.3', 'NDRG4', 'ACE2']
  rawTissues = [12, 36, 33, 34, 35, 47]

  gModel = GenesModel(genes)
  genecodeIds = gModel.getGencodeIds() # make sure input genes are converted to Gencode IDs.

  tModel = TissuesInfoModel()
  validTissues = tModel.getTissues('tissueSiteDetailId')
  tissueIds = [validTissues[int(id)] for id in rawTissues] # validate tissue

  # MedianGeneExpressionModel
  mModel = MedianGeneExpressionModel(genecodeIds, tissueIds)
  genes, medians = mModel.getMedianExpression()
  
  # make use of pands DataFrame
  df = pd.DataFrame(data=medians, index=genes) # 
  display(df)

  # https://pandas.pydata.org/pandas-docs/stable/user_guide/visualization.html
  plt = df.plot(kind='bar', title='Median Gene Expression', rot=0)
  plt.set(xlabel='Gene', ylabel='Median')

main()

# generate heatmap
# https://seaborn.pydata.org/generated/seaborn.heatmap.html#seaborn.heatmap
import seaborn # seaborn comes with anaconda :D
seaborn.heatmap(df, cmap='YlGnBu', linewidths=0.5, robust=True, annot=True)

