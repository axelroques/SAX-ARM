
import pandas as pd
import numpy as np


def SBGen(df_SAX, symb_top, symb_bottom, labels=None):
    """ Synbol Basket Generation Algorithm
      Input:
            param1 (symbolized[array(W x M)]):   Multivariate Time Series 
            param2 (symtop['string']):  Symbol of interest (from alphabet)
            param3 (symbottom['string']):  Symbol of interest (from alphabet)
      Returns:
            array
    """

    data = {
        'symb_basket_id': [],
        'time_series_id': [],
        'symbol': []
    }

    n_t, n_series = df_SAX.shape

    # Initialization
    B = []
    for i_t in range(n_t):
        b = []

        for i_series in range(n_series):
            symb = df_SAX.iloc[i_t, i_series]

            if symb in [symb_top, symb_bottom]:

                # If DataFrame has columns, keep the columns names
                # in the baskets. Otherwise keep integer index.
                if not(labels is None):
                    i_series = labels[i_series]

                b.append((i_series, symb))

                data['symb_basket_id'].append(i_t)
                data['time_series_id'].append(i_series)
                data['symbol'].append(symb)

        # Only add b if it is not empty
        if b:
            B.append(b)

    # Support for deviant events
    df = pd.DataFrame(data=data)
    supp = df.groupby(['time_series_id', 'symbol']).count()/n_t
    supp = supp.unstack(level=-1)
    supp.columns = supp.columns.droplevel(level=0)
    supp.columns.name = None

    # Depending on the choice of w and a, there may not be top or bottom symbols
    if (not(symb_top in data['symbol'])) and (not(symb_bottom in data['symbol'])):
        print('No maximal deviant symbols! Change parameters w or a for better rules.')
        return B, supp
    else:
        if not(symb_top in data['symbol']):
            supp[f'{symb_top}'] = np.zeros(len(supp))
            print('No maximal deviant symbol! Change parameters w or a for better rules.')
        if not(symb_bottom in data['symbol']):
            supp[f'{symb_bottom}'] = np.zeros(len(supp))
            print('No maximal deviant symbol! Change parameters w or a for better rules.')

    supp['Sum'] = supp[f'{symb_top}'] + supp[f'{symb_bottom}']
    supp = supp.rename(columns={f'{symb_top}': f'support({symb_top})',
                                f'{symb_bottom}': f'support({symb_bottom})'})

    return B, supp.sort_values('Sum', ascending=False)
