from pathlib import Path
import click
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from bs4 import BeautifulSoup

DOSIMETRIC_DATA_SOURCE = Path(Path(__file__).parent, 'data.h5')
HTML_TEMPLATE_FILE = Path(Path(__file__).parent, 'template.html')
HTML_OUTPUT_FILE = Path(Path(__file__).parent, 'site', 'index.html')


def data(data_path: Path) -> pd.DataFrame:
    return pd.DataFrame(pd.read_hdf(data_path, key='df'))


def summary_plot(df: pd.DataFrame) -> go.Figure:
    '''Plot the data'''
    fig = px.scatter(df,
                     x="first_timestamp",
                     y=["E1"],
                     title="Ionisation chamber current vs time",
                     color='driver',
                     render_mode='webgl')
    return fig


def driver_facets(df: pd.DataFrame) -> go.Figure:
    '''Plot the data'''
    fig = px.scatter(df,
                     x="first_timestamp",
                     y=["E1"],
                     title="Ionisation chamber current vs time",
                     facet_col='driver',
                     render_mode='webgl')
    return fig


@click.command()
def generate() -> None:
    '''Generate the plot and save it to a file'''
    df = data(DOSIMETRIC_DATA_SOURCE)
    # parse the template file using beautiful soup
    with open(HTML_TEMPLATE_FILE, 'r') as f:
        click.echo(f'Parsing {HTML_TEMPLATE_FILE}')
        soup = BeautifulSoup(f, 'html.parser')

        summary_template_div = soup.find(id='plot-tabs-1')
        if summary_template_div is not None:
            fig = summary_plot(df)
            plot_div = fig.to_html(fig,
                                   include_plotlyjs='cdn',
                                   full_html=False,
                                   default_height='80%',
                                   default_width='90%')
            summary_template_div.append(BeautifulSoup(plot_div, 'html.parser'))

        driver_template_div = soup.find(id='plot-tabs-3')
        if driver_template_div is not None:
            fig = driver_facets(df)
            plot_div = fig.to_html(fig,
                                   include_plotlyjs='cdn',
                                   full_html=False,
                                   default_height='80%',
                                   default_width='90%')
            driver_template_div.append(BeautifulSoup(plot_div, 'html.parser'))

        # ensure the output directory exists
        HTML_OUTPUT_FILE.parent.mkdir(exist_ok=True, parents=True)
        # write the output file
        with open(HTML_OUTPUT_FILE, 'w') as f:
            click.echo(f'Writing {HTML_OUTPUT_FILE}')
            f.write(str(soup))


@click.command()
@click.option('--plot',
              type=click.Choice(['summary', 'driver']),
              default='summary',
              help='Plot to show')
def show(plot) -> None:
    '''Show the plot in a browser'''
    df = data(DOSIMETRIC_DATA_SOURCE)
    fig = go.Figure()
    click.echo(f'Plotting {plot}')
    if plot == 'driver':
        fig = driver_facets(df)
    elif plot == 'summary':
        fig = summary_plot(df)
    fig.show()


@click.group()
def run():
    pass


run.add_command(show)
run.add_command(generate)

if __name__ == "__main__":
    run()
