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


def conditions(data_path: Path) -> tuple[pd.DataFrame, dict]:
    metadata = {}
    with pd.HDFStore(data_path, mode='r') as store:
        metadata = store.get_storer('conditions').attrs.metadata

    return pd.DataFrame(pd.read_hdf(data_path, key='conditions')), metadata


def summary_plot(df: pd.DataFrame) -> go.Figure:
    '''Plot the data'''
    fig = px.scatter(df,
                     x="timestamp",
                     y=["E1"],
                     title="Ionisation chamber current vs time",
                     color='driver',
                     render_mode='webgl')
    return fig


def figure_experiments(df: pd.DataFrame, time_shift: pd.Timedelta = pd.Timedelta('0s')) -> list[go.Figure]:
    '''Plot the data'''

    figs = []
    df_with_experiments = df[df.experiment != 'unknown'].copy(deep=True)
    df_with_experiments['timestamp'] += time_shift
    experiment_names = df_with_experiments.experiment.unique()

    for experiment_name in experiment_names:

        fig = px.scatter(df_with_experiments[df_with_experiments.experiment == experiment_name],
                         x="timestamp",
                         y=["E1"],
                         title="Ionisation chamber current vs time",
                         facet_col='experiment',
                         color='scenario',
                         render_mode='webgl')
        fig.update_xaxes(matches=None)

        scenario_labels = df_with_experiments[df_with_experiments.experiment == experiment_name].scenario.unique()
        buttons = [
            dict(label=scenario_label,
                 method='update',
                 args=[{
                     'visible': [scenario_label == item for item in scenario_labels]
                 }, {
                     'title': scenario_label,
                     'showlegend': True
                 }]) for scenario_label in scenario_labels
        ]
        if len(scenario_labels) > 1:
            buttons.append(
                dict(label='All',
                    method='update',
                    args=[{
                        'visible': [True for _ in scenario_labels]
                    }, {
                        'title': 'All',
                        'showlegend': True
                    }]))

        fig.update_layout(updatemenus=[dict(
            buttons=buttons,
            active=0,
            type="buttons",
            direction="down",
        )])

        figs.append(fig)
    return figs


@click.command()
def generate() -> None:
    '''Generate the plot and save it to a file'''
    df = data(DOSIMETRIC_DATA_SOURCE)

    df_conditions, conditions_metadata = conditions(DOSIMETRIC_DATA_SOURCE)
    print(conditions_metadata)

    # parse the template file using beautiful soup
    with open(HTML_TEMPLATE_FILE, 'r') as f:
        click.echo(f'Parsing {HTML_TEMPLATE_FILE}')
        soup = BeautifulSoup(f, 'html.parser')

        template_div = soup.find(id='plot-tabs-1')
        if template_div is not None:
            experiment_figs = figure_experiments(df)
            for experiment_fig in experiment_figs:
                experiment_plot_div_1 = experiment_fig.to_html(experiment_fig,
                                                             include_plotlyjs='cdn',
                                                             full_html=False,
                                                             default_height='80%',
                                                             default_width='90%')
                template_div.append(BeautifulSoup(experiment_plot_div_1, 'html.parser'))

            # write the output file
            with open(HTML_OUTPUT_FILE, 'w') as f:
                click.echo(f'Writing {HTML_OUTPUT_FILE}')
                f.write(str(soup))
            # print the size of output file in MBs
            click.echo(f'Output file {HTML_OUTPUT_FILE} size: {HTML_OUTPUT_FILE.stat().st_size / 1024 / 1024:3.3f} MBs')
            template_div.clear()


            experiment_figs = figure_experiments(df, time_shift = conditions_metadata['lgad_time_shift_ref'])
            for experiment_fig in experiment_figs:
                experiment_plot_div_2 = experiment_fig.to_html(experiment_fig,
                                                             include_plotlyjs='cdn',
                                                             full_html=False,
                                                             default_height='80%',
                                                             default_width='90%')
                template_div.append(BeautifulSoup(experiment_plot_div_2, 'html.parser'))
            # write the output file
            output_filename = HTML_OUTPUT_FILE.with_name('tab2.html')
            with open(output_filename, 'w') as f:
                click.echo(f"Writing {output_filename}")
                f.write(str(soup))
            # print the size of output file in MBs
            click.echo(f"Output file {output_filename} size: {output_filename.stat().st_size / 1024 / 1024:3.3f} MBs")
            template_div.clear()


            experiment_figs = figure_experiments(df, time_shift = conditions_metadata['lgad_time_shift_data'])
            for experiment_fig in experiment_figs:
                experiment_plot_div_2 = experiment_fig.to_html(experiment_fig,
                                                             include_plotlyjs='cdn',
                                                             full_html=False,
                                                             default_height='80%',
                                                             default_width='90%')
                template_div.append(BeautifulSoup(experiment_plot_div_2, 'html.parser'))
            # write the output file
            output_filename = HTML_OUTPUT_FILE.with_name('tab3.html')
            with open(output_filename, 'w') as f:
                click.echo(f"Writing {output_filename}")
                f.write(str(soup))
            # print the size of output file in MBs
            click.echo(f"Output file {output_filename} size: {output_filename.stat().st_size / 1024 / 1024:3.3f} MBs")
            template_div.clear()


            # rename column name file_creation_timestamp to file_creation
            df_conditions.rename(columns={
                "file_creation_timestamp": "file_creation",
                "stage1_timestamp": "stage1",
                "stage2_timestamp": "stage2",
                "stage3_timestamp": "stage3",
                "stage4_timestamp": "stage4",
                "no_of_measurements": "no_of_meas"
            },
                                 inplace=True)
            df_conditions["day"] = df_conditions["file_creation"].dt.strftime("%Y-%m-%d")
            df_conditions["time_window"] = df_conditions["time_window"].apply(lambda x: x.total_seconds())

            # drop rows with unknown experiment or scenario
            df_conditions.drop(df_conditions[(df_conditions.experiment == 'unknown') |
                                             (df_conditions.scenario == 'unknown')].index,
                               inplace=True)

            df_conditions.set_index(['experiment', 'scenario', 'file_creation'], inplace=True)
            df_conditions.sort_index(inplace=True)
            df_conditions.reset_index(inplace=True)

            df_conditions.set_index(['experiment', 'scenario'], inplace=True)

            df_conditions.insert(0, "day", df_conditions.pop("day"))
            df_conditions.insert(2, "stage1", df_conditions.pop("stage1"))
            df_conditions.insert(3, "stage2", df_conditions.pop("stage2"))
            df_conditions.insert(4, "stage3", df_conditions.pop("stage3"))
            df_conditions.insert(5, "stage4", df_conditions.pop("stage4"))

            conditions_div = df_conditions.to_html(show_dimensions=True,
                                                   classes='table table-striped table-hover table-sm',
                                                   formatters={
                                                       'file_creation': lambda x: x.strftime('%H:%M:%S'),
                                                       'stage1': lambda x: x.strftime('%H:%M:%S.%f')[:-5],
                                                       'stage2': lambda x: x.strftime('%H:%M:%S.%f')[:-5],
                                                       'stage3': lambda x: x.strftime('%H:%M:%S.%f')[:-5],
                                                       'stage4': lambda x: x.strftime('%H:%M:%S.%f')[:-5],
                                                   })
            template_div.append(BeautifulSoup(conditions_div, 'html.parser'))
            # write the output file
            output_filename = HTML_OUTPUT_FILE.with_name('tab4.html')
            with open(output_filename, 'w') as f:
                click.echo(f"Writing {output_filename}")
                f.write(str(soup))
            # print the size of output file in MBs
            click.echo(f"Output file {output_filename} size: {output_filename.stat().st_size / 1024 / 1024:3.3f} MBs")
            template_div.clear()


@click.command()
@click.option('--plot', type=click.Choice(['summary', 'experiment']), default='experiment', help='Plot to show')
@click.option('--experiment_no', type=int, default=0, help='Experiment number to show')
def show(plot, experiment_no: int) -> None:
    '''Show the plot in a browser'''
    df = data(DOSIMETRIC_DATA_SOURCE)
    fig = go.Figure()
    click.echo(f'Plotting {plot}')
    if plot == 'experiment':
        fig = figure_experiments(df)[experiment_no]
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
