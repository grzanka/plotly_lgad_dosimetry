from pathlib import Path
import requests
import pandas as pd
import plotly.express as px

from io import StringIO


DOSIMETRIC_DATA_URL = "https://gist.githubusercontent.com/grzanka/ac78b7aaea89ec94ac8692842778569e/raw/23e988abb7d7892cb13b3937b296ff79a0b474ee/gistfile2.txt"

def fetch_csv(data_url: str) -> pd.DataFrame:
    return pd.read_csv(StringIO(requests.get(data_url).text))

def plot(df: pd.DataFrame, outfile: Path):
    fig = px.scatter(
        df,
        x="first_timestamp",
        y=["E1"],
        title="Test",
        color='filename_core',
        facet_col="driver",
        render_mode='webgl'
    )
#    fig.update_traces(marker_line=dict(width=1, color='DarkSlateGray'))
    fig.write_html(str(outfile), include_plotlyjs='cdn')
    #fig.show()

if __name__ == "__main__":
    df = fetch_csv(DOSIMETRIC_DATA_URL)
    print(df.head())

    outfile = Path("site", "index.html")
    outfile.parent.mkdir(exist_ok=True, parents=True)
    plot(df, outfile)
