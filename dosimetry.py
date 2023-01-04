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
    click.echo(f'Reading {data_path}')
    return pd.DataFrame(pd.read_hdf(data_path, key='data'))


def conditions(data_path: Path) -> tuple[pd.DataFrame, dict]:
    click.echo(f'Reading {data_path} conditions')
    metadata = {}
    with pd.HDFStore(data_path, mode='r') as store:
        metadata = store.get_storer('conditions').attrs.metadata

    return pd.DataFrame(pd.read_hdf(data_path, key='conditions')), metadata


def summary_html_element(df: pd.DataFrame) -> str:
    '''Generate the summary table as an html element'''

    df_conditions = df.copy()
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
    # drop rows without timestamp
    df_conditions.dropna(subset=['file_creation'], inplace=True)

    df_conditions.set_index(['experiment', 'scenario'], inplace=True)
    df_conditions.sort_values(by=['experiment', 'file_creation'], inplace=True)

    df_conditions.insert(0, "day", df_conditions.pop("day"))
    df_conditions.insert(1, "file_creation", df_conditions.pop("file_creation"))
    df_conditions.insert(2, "stage1", df_conditions.pop("stage1"))
    df_conditions.insert(3, "stage2", df_conditions.pop("stage2"))
    df_conditions.insert(4, "stage3", df_conditions.pop("stage3"))
    df_conditions.insert(5, "stage4", df_conditions.pop("stage4"))

    html_element = df_conditions.to_html(show_dimensions=True,
                                         classes='table table-striped table-hover table-sm',
                                         formatters={
                                             'file_creation': lambda x: x.strftime('%H:%M:%S'),
                                             'stage1': lambda x: x.strftime('%H:%M:%S.%f')[:-5],
                                             'stage2': lambda x: x.strftime('%H:%M:%S.%f')[:-5],
                                             'stage3': lambda x: x.strftime('%H:%M:%S.%f')[:-5],
                                             'stage4': lambda x: x.strftime('%H:%M:%S.%f')[:-5],
                                         })
    return html_element


def summary_plot(df: pd.DataFrame) -> go.Figure:
    '''Plot the data'''
    fig = px.scatter(df,
                     x="timestamp",
                     y=["E1"],
                     title="Ionisation chamber current vs time",
                     color='driver',
                     render_mode='webgl')
    return fig


def figures_for_experiment(df: pd.DataFrame, time_shift: pd.Timedelta = pd.Timedelta('0s')) -> go.Figure:
    '''Plot the data'''

    df_to_plot = df.copy()
    df_to_plot['timestamp'] += time_shift
    fig = px.scatter(df_to_plot,
                     x="timestamp",
                     y=["E1"],
                     title="Ionisation chamber current vs time",
                     facet_col='experiment',
                     color='scenario',
                     render_mode='webgl')
    fig.update_xaxes(matches=None)

    scenario_labels = df_to_plot.scenario.unique()
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

    return fig


def save_single_html(output_path: Path, html_element: str, soup: BeautifulSoup) -> None:
    template_div = soup.find(id='content-div')
    if template_div:
        # ensure the output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            click.echo(f"Writing {output_path}")
            template_div.append(BeautifulSoup(html_element, 'html.parser'))
            f.write(str(soup))
        # print the size of output file in MBs
        click.echo(f"Output file {output_path} size: {output_path.stat().st_size / 1024 / 1024:3.3f} MBs")
        if template_div:
            template_div.clear()


@click.command()
def generate() -> None:
    '''Generate the plot and save it to a file'''
    df = data(DOSIMETRIC_DATA_SOURCE)
    df_conditions, conditions_metadata = conditions(DOSIMETRIC_DATA_SOURCE)

    # parse the template file using beautiful soup
    with open(HTML_TEMPLATE_FILE, 'r') as f:
        click.echo(f'Parsing {HTML_TEMPLATE_FILE}')
        soup = BeautifulSoup(f, 'html.parser')

        experiment_names = df_conditions.experiment.unique().tolist()
        # remove 'unknown' experiment
        experiment_names.remove('unknown')
        click.echo(f'Found {len(experiment_names)} experiments: {experiment_names}')

        for experiment_name in experiment_names:
            click.echo(f'Processing experiment {experiment_name}')

        ul_element = soup.find(id='plot-list-1')
        for experiment_name in experiment_names:
            li_element = soup.new_tag('li', **{'class': 'nav-item', 'role': 'presentation'})
            a_element = soup.new_tag('a',
                                     href=f'{experiment_name}.html',
                                     **{
                                         'class': 'nav-link',
                                         'role': 'tab',
                                         'data-toggle': 'tab'
                                     })
            a_element.string = experiment_name
            li_element.append(a_element)
            ul_element.append(li_element)

        # add the summary table
        save_single_html(HTML_OUTPUT_FILE.with_name('index.html'), summary_html_element(df_conditions), soup)

        for experiment_name in experiment_names:
            df_experiment = df[df.experiment == experiment_name]
            all_fig_html_elem = ""
            timeshifts = {
                'IFJ time shift': pd.Timedelta('0s'),
                'LGAD time ref': conditions_metadata['lgad_time_shift_ref'],
                'LGAD time data': conditions_metadata['lgad_time_shift_data']
            }

            ul_element = soup.new_tag('ul', **{'class': 'nav nav-pills', 'role': 'tablist'})
            for timeshift_name, timeshift in timeshifts.items():
                li_element = soup.new_tag('li', **{'class': 'nav-item', 'role': 'presentation'})
                a_element = soup.new_tag('a',
                                         href=f'#{timeshift_name.strip().replace(" ", "-")}',
                                         onclick="window.dispatchEvent(new Event('resize'));",
                                         **{
                                             'class': 'nav-link',
                                             'role': 'tab',
                                             'data-mdb-toggle': 'pill'
                                         })
                if timeshift_name == 'IFJ time shift':
                    a_element['class'] = 'nav-link active'
                a_element.string = timeshift_name
                li_element.append(a_element)
                ul_element.append(li_element)
            all_fig_html_elem += str(ul_element)

            div_element = soup.new_tag('div', **{'class': 'tab-content'})
            for timeshift_name, timeshift in timeshifts.items():
                div_element_timeshift = soup.new_tag('div',
                                                     id=f'{timeshift_name.strip().replace(" ", "-")}',
                                                     **{
                                                         'class': 'tab-pane fade',
                                                         'role': 'tabpanel'
                                                     })
                if timeshift_name == 'IFJ time shift':
                    div_element_timeshift['class'] = 'tab-pane fade show active'
                exp_figure = figures_for_experiment(df_experiment, time_shift=timeshift)
                div_description = soup.new_tag('div', **{'class': 'description'})
                div_description.string = f'Experiment {experiment_name} with {timeshift_name}'
                div_element_timeshift.append(div_description)
                div_element_timeshift.append(
                    BeautifulSoup(
                        exp_figure.to_html(include_plotlyjs='cdn',
                                           full_html=False,
                                           default_height='80%',
                                           default_width='90%'), 'html.parser'))
                div_element.append(div_element_timeshift)
            all_fig_html_elem += str(div_element)

            save_single_html(HTML_OUTPUT_FILE.with_name(f'{experiment_name}.html'), all_fig_html_elem, soup)


@click.command()
@click.option('--plot', type=click.Choice(['summary', 'experiment']), default='experiment', help='Plot to show')
@click.option('--experiment_no', type=int, default=0, help='Experiment number to show')
def show(plot, experiment_no: int) -> None:
    '''Show the plot in a browser'''
    df = data(DOSIMETRIC_DATA_SOURCE)
    fig = go.Figure()
    click.echo(f'Plotting {plot}')
    if plot == 'experiment':
        fig = figures_for_experiment(df[df.experiment == 'current_scan'])
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
