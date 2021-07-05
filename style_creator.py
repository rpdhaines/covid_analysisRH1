# container for helper functions to quickly set styles

def create_div_style(mb=5, mt=5, ml=5, mr=5, fs=12, c='black', w='100%', display='block', va='top', float='left',
                     borderb=None):

    style_dict = {'margin-bottom': f'{mb}px',
                  'margin-top': f'{mt}px',
                  'margin-left': f'{ml}px',
                  'margin-right': f'{mr}px',
                  'fontSize': fs,
                  'color': c,
                  'width': w,
                  'display': display,
                  'verticalAlign': va,
                  'float': float,
                  'border-bottom': borderb
                  }

    return style_dict

def create_graph_layout(title, xtitle, ytitle, height=400,
                        marginl=40, marginr=0, marginb=40, margint=30,
                        colour='white'):
    """
    helper function to create graph layout defaulting to preferred standard parameters
    :param title: str - title of graph
    :param xtitle: str - title of x-axis
    :param ytitle: str - title of y-axis
    :param height: int - height of figure
    :param marginl: int - left margin
    :param marginr: int - right margin
    :param marginb: int - bottom margin
    :param margint: int - top margin
    :param colour: str - background colour
    :return: layout dictionary to be used in fig.update_layout
    """

    layout_dict = dict(
        xaxis={
            'title': xtitle,
            'gridcolor': 'lightgrey'
        },
        yaxis={
            'title': ytitle,
            'gridcolor': 'lightgrey'
        },
        title={'text': title,
               'x': 0.5, 'y': 0.98},
        margin={'l': marginl, 'b': marginb, 't': margint, 'r': marginr},
        hovermode='closest',
        plot_bgcolor=colour,
        height=height,
        legend = {'yanchor': "top", 'y': 0.99, 'xanchor': "left", 'x': 0.01},
        showlegend = True
    )

    return layout_dict