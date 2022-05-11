import logging
from unittest import TestCase

from pyGTEx.models import TissuesInfoModel


logger = logging.getLogger(__name__)


class ModelsTests(TestCase):
    """
    Test suite for the GTEx model API.
    """

    def test_tissues_info_model(self):
        # specify tissue site, should return tissues related to the given site
        model = TissuesInfoModel(tissueSite="Colon")
        self.assertEqual(model.getTissues("tissueSiteDetail"), ['Colon - Sigmoid', 'Colon - Transverse'])
