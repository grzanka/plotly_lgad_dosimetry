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


def plot(df: pd.DataFrame) -> go.Figure:
    '''Plot the data'''
    fig = px.scatter(df,
                     x="first_timestamp",
                     y=["E1"],
                     title="Ionisation chamber current vs time",
                     facet_col="driver",
                     render_mode='webgl')
    return fig


@click.command()
def full() -> None:
    '''Generate the plot and save it to a file'''
    df = data(DOSIMETRIC_DATA_SOURCE)
    fig = plot(df)
    outfile = Path("site", "index.html")
    outfile.parent.mkdir(exist_ok=True, parents=True)
    plot_div = fig.to_html(fig, include_plotlyjs='cdn', full_html=True)
    # parse the `site/index.html` file using beautiful soup
    with open(HTML_TEMPLATE_FILE, 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')
        template_div = soup.find(id='ex1-tabs-1')
        if template_div is not None:
            template_div.append(BeautifulSoup(plot_div, 'html.parser'))
        with open(HTML_OUTPUT_FILE, 'w') as f:
            f.write(str(soup))


@click.command()
def generate() -> None:
    '''Generate the plot and save it to a file'''
    df = data(DOSIMETRIC_DATA_SOURCE)
    fig = plot(df)
    outfile = Path("site", "index.html")
    outfile.parent.mkdir(exist_ok=True, parents=True)
    fig.write_html(str(outfile), include_plotlyjs='cdn')


@click.command()
def show() -> None:
    '''Show the plot in a browser'''
    df = data(DOSIMETRIC_DATA_SOURCE)
    fig = plot(df)
    fig.show()


@click.group()
def run():
    pass


run.add_command(show)
run.add_command(generate)
run.add_command(full)

if __name__ == "__main__":
    run()
