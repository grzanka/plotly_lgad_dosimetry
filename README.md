# plotly_lgad_dosimetry

## Working with the code

Create python virtual environment to handle all required dependencies in the project directory:

```
python3 -m venv venv
source venv/bin/activate
```

For Windows activate by running in Powershell: `.\venv\Scripts\Activate.ps1`.
According to stack overflow, you need setuptools>=62 and pip>=21.3 to be able to install the requirements.

We use `requirements.txt` file to specify all required dependencies:

```
pip install -r requirements.txt
```

Once you are done deactivate the virtual environment:

```
deactivate
```

## Running the code

To generate the static HTML file with the plotly graphs run:

```
python dosimetry.py generate
```

To show the plot in the browser run:

```
python dosimetry.py show
```