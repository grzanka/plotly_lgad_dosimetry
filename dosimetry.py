from pathlib import Path
import click
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DOSIMETRIC_DATA_SOURCE = Path(Path(__file__).parent, 'data.h5')


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

if __name__ == "__main__":
    run()
