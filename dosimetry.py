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
    return pd.DataFrame(pd.read_hdf(data_path, key='data'))


def summary_plot(df: pd.DataFrame) -> go.Figure:
    '''Plot the data'''
    fig = px.scatter(df,
                     x="timestamp",
                     y=["E1"],
                     title="Ionisation chamber current vs time",
                     color='driver',
                     render_mode='webgl')
    return fig


def driver_facets(df: pd.DataFrame) -> go.Figure:
    '''Plot the data'''
    fig = px.scatter(df,
                     x="timestamp",
                     y=["E1"],
                     title="Ionisation chamber current vs time",
                     facet_col='driver',
                     render_mode='webgl')
    return fig


def figure_experiments(df: pd.DataFrame, time_column: str = "timestamp") -> list[go.Figure]:
    '''Plot the data'''

    figs = []
    df_with_experiments = df[df.experiment != 'unknown']

    experiment_names = df_with_experiments.experiment.unique()

    for experiment_name in experiment_names:
        fig = px.scatter(df_with_experiments[df_with_experiments.experiment ==
                                             experiment_name],
                         x=time_column,
                         y=["E1"],
                         title="Ionisation chamber current vs time",
                         facet_col='experiment',
                         color='scenario',
                         render_mode='webgl')
        fig.update_xaxes(matches=None)

        scenario_labels = df_with_experiments[
            df_with_experiments.experiment ==
            experiment_name].scenario.unique()
        buttons = [
            dict(label=scenario_label,
                 method='update',
                 args=[{
                     'visible':
                     [scenario_label == item for item in scenario_labels]
                 }, {
                     'title': scenario_label,
                     'showlegend': True
                 }]) for scenario_label in scenario_labels
        ]
        buttons.append(
            dict(label='All',
                 method='update',
                 args=[{
                     'visible': [True for item in scenario_labels]
                 }, {
                     'title': 'All',
                     'showlegend': True
                 }]))

        fig.update_layout(updatemenus=[
            dict(
                buttons=buttons,
                active=0,
                type="buttons",
                direction="down",
            )
        ])
        figs.append(fig)
    return figs


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
            summary_fig = summary_plot(df)
            summary_plot_div = summary_fig.to_html(summary_fig,
                                                   include_plotlyjs='cdn',
                                                   full_html=False,
                                                   default_height='80%',
                                                   default_width='90%')
            summary_template_div.append(
                BeautifulSoup(summary_plot_div, 'html.parser'))

        experiment_template_div = soup.find(id='plot-tabs-2')
        if experiment_template_div is not None:
            experiment_figs = figure_experiments(df)
            for experiment_fig in experiment_figs:
                experiment_plot_div = experiment_fig.to_html(
                    experiment_fig,
                    include_plotlyjs='cdn',
                    full_html=False,
                    default_height='80%',
                    default_width='90%')
                experiment_template_div.append(
                    BeautifulSoup(experiment_plot_div, 'html.parser'))

        # driver_template_div = soup.find(id='plot-tabs-3')
        # if driver_template_div is not None:
        #     driver_fig = driver_facets(df)
        #     driver_plot_div = driver_fig.to_html(driver_fig,
        #                                          include_plotlyjs='cdn',
        #                                          full_html=False,
        #                                          default_height='80%',
        #                                          default_width='90%')
        #     driver_template_div.append(
        #         BeautifulSoup(driver_plot_div, 'html.parser'))

        # experiment_template_div = soup.find(id='plot-tabs-4')
        # if experiment_template_div is not None:
        #     experiment_figs = figure_experiments(df, time_column="lgad_timestamp")
        #     for experiment_fig in experiment_figs:
        #         experiment_plot_div = experiment_fig.to_html(
        #             experiment_fig,
        #             include_plotlyjs='cdn',
        #             full_html=False,
        #             default_height='80%',
        #             default_width='90%')
        #         experiment_template_div.append(
        #             BeautifulSoup(experiment_plot_div, 'html.parser'))

        # experiment_template_div = soup.find(id='plot-tabs-5')
        # if experiment_template_div is not None:
        #     experiment_figs = figure_experiments(df, time_column="lgad_timestamp_data")
        #     for experiment_fig in experiment_figs:
        #         experiment_plot_div = experiment_fig.to_html(
        #             experiment_fig,
        #             include_plotlyjs='cdn',
        #             full_html=False,
        #             default_height='80%',
        #             default_width='90%')
        #         experiment_template_div.append(
        #             BeautifulSoup(experiment_plot_div, 'html.parser'))

        # ensure the output directory exists
        HTML_OUTPUT_FILE.parent.mkdir(exist_ok=True, parents=True)
        # write the output file
        with open(HTML_OUTPUT_FILE, 'w') as f:
            click.echo(f'Writing {HTML_OUTPUT_FILE}')
            f.write(str(soup))


@click.command()
@click.option('--plot',
              type=click.Choice(['summary', 'driver', 'experiment']),
              default='summary',
              help='Plot to show')
def show(plot) -> None:
    '''Show the plot in a browser'''
    df = data(DOSIMETRIC_DATA_SOURCE)
    fig = go.Figure()
    click.echo(f'Plotting {plot}')
    if plot == 'driver':
        fig = driver_facets(df)
    elif plot == 'experiment':
        fig = figure_experiments(df)[0]
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
