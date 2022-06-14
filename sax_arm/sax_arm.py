
from .apriori import apriori
from .symbol_basket import SBGen

from sax import SAX


class SAX_ARM:

    def __init__(self, df,  w=3, a=4, min_supp=0.01, min_conf=0.5):

        # Raw data
        self.df = df

        # SAX parameters
        self.sax = SAX(df, w=w, a=a, alphabet_type='letters')

        # Apriori parameters
        self.min_supp = min_supp
        self.min_conf = min_conf

    def process(self):
        """
        Run the SAX-ARM algorithm process. 
        """

        # SAX discretization
        self.sax.process()

        # Symbol basket generation
        self.B, self.support = SBGen(self.sax.df_SAX,
                                     self.sax.alphabet[-1],
                                     self.sax.alphabet[0],
                                     self.sax.df_SAX.columns)

        # Apriori algorithm
        self.rules = apriori(self.B, min_supp=self.min_supp,
                             min_conf=self.min_conf)

        return

    def get_support(self):
        """
        Return the support of the deviant evants.
        """
        return self.support

    def get_rules(self):
        """
        Return the association rules.
        """
        return self.rules
