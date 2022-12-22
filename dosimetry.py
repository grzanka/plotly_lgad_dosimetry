from pathlib import Path
import requests
import pandas as pd
import plotly.express as px

from io import StringIO


#DOSIMETRIC_DATA_URL = "https://gist.githubusercontent.com/grzanka/ac78b7aaea89ec94ac8692842778569e/raw/2052f7e84e31d993d5dac06c448af3e963b9cbfa/file.csv"
DOSIMETRIC_DATA_URL = "https://raw.githubusercontent.com/CITF-Malaysia/citf-public/main/vaccination/vax_state.csv"


def fetch_csv(data_url: str) -> pd.DataFrame:
    return pd.read_csv(StringIO(requests.get(data_url).text))


def clean(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.set_index(["date", "state"])
        .loc[:, ["cumul_partial", "cumul_full", "cumul"]]
        .rename(columns={"cumul_partial": "partially_vaxed", "cumul_full": "fully_vaxed"})
        .sort_values(by="cumul", ascending=False)
        .sort_index(level="date", sort_remaining=False)
        .reset_index()
    )


def plot_cumulative_state(df: pd.DataFrame, outfile: Path):
    fig = px.bar(
        state_data,
        x="state",
        y=["partially_vaxed", "fully_vaxed"],
        animation_frame="date",
        animation_group="state",
        labels={"value": "Total vaccinated", "state": "", "variable": "Dose Type"},
        title="Vaccination Count in Malaysia by State",
    )

    fig.write_html(str(outfile), include_plotlyjs='cdn')


if __name__ == "__main__":
    state_data = fetch_csv(DOSIMETRIC_DATA_URL)
    state_data = clean(state_data)

    outfile = Path("site", "index.html")
    outfile.parent.mkdir(exist_ok=True, parents=True)
    plot_cumulative_state(state_data, outfile)