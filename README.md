# Pygtex

Our program is implemented in Python. Packages including urllib, json, and ssl from the Python Standard Library are used to retrieve and process results returned from the GTEx REST API. The API returns data in JSON format with a consistent structure. A representation of this structure is encapsulated inside a Model class and then parsed inside specific subclasses of this structure after it is retrieved from the API. The GTEx API is used to retrieve unique matching Gencode IDs given a query containing gene symbols or unversioned Gencode IDs from the GRCh38/hg38 genome assembly. The Gencode IDs can then be served as an identifier to access the rest of the API such as median gene expression data across selected genes. 

