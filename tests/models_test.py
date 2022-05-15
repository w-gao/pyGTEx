import logging
from unittest import TestCase

from pyGTEx.models import TissuesInfoModel, GeneModel, GenesModel

logger = logging.getLogger(__name__)


class ModelsTests(TestCase):
    """
    Test suite for the GTEx model API using the HG38 genome build version.
    """

    def test_tissues_info_model(self):
        # specify tissue site, should return tissues related to the given site
        model = TissuesInfoModel(tissueSite="Colon")
        self.assertEqual(model.getTissues("tissueSiteDetail"), ['Colon - Sigmoid', 'Colon - Transverse'])

    def test_gene_model(self):
        model = GeneModel(geneId="ACE2")
        model_from_id = GeneModel(geneId="ENSG00000130234")
        model_from_versioned_id = GeneModel(geneId="ENSG00000130234.10")

        # all three queries should yield the same ACE2 gene
        self.assertEqual(model.data, model_from_id.data)
        self.assertEqual(model_from_id.data, model_from_versioned_id.data)

        self.assertEqual(model.getDescription(),
                         "angiotensin I converting enzyme 2 [Source:HGNC Symbol;Acc:HGNC:13557]")

        self.assertEqual(model.getGeneSymbol(), "ACE2")
        self.assertEqual(model.getGencodeId(), "ENSG00000130234.10")
        self.assertEqual(model.getEntrezGeneId(), 59272)

    def test_genes_model(self):
        model = GenesModel(geneIds=["ACE", "ACE2"])
        self.assertEqual(model.getGeneSymbols(), ["ACE", "ACE2"])
        self.assertEqual(model.getGencodeIds(), ["ENSG00000159640.15", "ENSG00000130234.10"])


class HG19ModelsTests(TestCase):
    """
    Tests HG19 genome build version support.
    """

    def test_genes_model(self):
        model = GenesModel(geneIds=["ACE", "ACE2"], gencodeVersion="v19", genomeBuild="GRCh37/hg19")
        self.assertEqual(model.getGencodeIds(),
                         ["ENSG00000159640.10", "ENSG00000264813.1", "ENSG00000130234.6"])
