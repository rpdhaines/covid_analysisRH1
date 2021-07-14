# container for helper functions to quickly set styles

def create_div_style(mb=3, mt=3, ml=5, mr=5, fs=12, c='black', w='100%', display='block', va='top', float='left',
                     borderb=None, bordert=None, borderl=None, borderr=None, bc=None, gradient=None):
    """
    creates a style dictionary with some of the most common style elements I vary, together with setting others
    to sensible defaults. all parameters are style attributes as follows
    :param mb: Int - bottom margin
    :param mt: Int - top margin
    :param ml: Int - left margin
    :param mr: Int - right margin
    :param fs: Int - font size
    :param c: Str - colour. needs to be in form recognised by style dictionary
    :param w: Str - Width - set as a strng between '1% and '100%'
    :param display: Str - display
    :param va: Str - vertical align
    :param float: Str - float. i generally use to left or right align
    :param borderb: Str - border bottom. expects a 3 word string eg 'black solid 1px'
    :param bordert: Str - border top. expects a 3 word string eg 'black solid 1px'
    :param borderl: Str - border left. expects a 3 word string eg 'black solid 1px'
    :param borderr: Str - border right. expects a 3 word string eg 'black solid 1px'
    :param bc: Str - background colour. needs to be in a form recognised by the style dictionary
    :param gradient: Str - set background colour as image gradient between 2 colours - eg
    'linear-gradient(to right, #008080, #FFFFFF)'
    :return: Dict - in the form expected to be passed to the syle attribute of a Div box and some other boxes
    """

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
                  'border-bottom': borderb,
                  'border-top': bordert,
                  'border-left': borderl,
                  'border-right': borderr,
                  'background-color': bc,
                  'background-image': gradient
                  }

    return style_dict

def create_graph_layout(title, xtitle, ytitle, height=350,
                        marginl=40, marginr=0, marginb=40, margint=30,
                        colour='white', showlegend=True):
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
    :param showlegend: Boolean - if True, forces legend to show, even if only 1 trace line
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
        legend={'yanchor': "top", 'y': 0.99, 'xanchor': "left", 'x': 0.01},
        showlegend=showlegend
    )

    return layout_dict