# %%
import requests
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet


def get_eia_heating_oil_prices(api_key):
    """
    Descarga precios semanales de heating oil residencial para New York desde EIA.

    Unidad:
        dollars per gallon
    """

    url = "https://api.eia.gov/v2/petroleum/pri/wfr/data/"

    params = {
        "api_key": api_key,
        "frequency": "weekly",
        "data[]": "value",
        "facets[series][]": "W_EPD2F_PRS_SNY_DPG",
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": 10000,
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(response.text)
        response.raise_for_status()

    data = response.json()["response"]["data"]

    df = pd.DataFrame(data)

    if df.empty:
        raise ValueError("La API no devolvió datos. Revisa la API key o el código de serie.")

    df = df[["period", "value"]].copy()
    df["ds"] = pd.to_datetime(df["period"])
    df["y"] = pd.to_numeric(df["value"], errors="coerce")

    df = df[["ds", "y"]].dropna().sort_values("ds")

    return df


def forecast_annual_heating_oil_price(api_key, years=15):
    """
    Entrena Prophet con precios semanales de heating oil
    y devuelve la predicción promedio anual para los próximos años.
    """

    df = get_eia_heating_oil_prices(api_key)

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.05
    )

    model.fit(df)

    future = model.make_future_dataframe(
        periods=years * 52,
        freq="W"
    )

    forecast = model.predict(future)

    last_date = df["ds"].max()
    last_year = df["ds"].dt.year.max()

    forecast_future = forecast[forecast["ds"] > last_date].copy()
    forecast_future["year"] = forecast_future["ds"].dt.year

    forecast_annual = (
        forecast_future
        .groupby("year")
        .agg(
            predicted_dollars_per_gallon=("yhat", "mean"),
            lower_dollars_per_gallon=("yhat_lower", "mean"),
            upper_dollars_per_gallon=("yhat_upper", "mean"),
        )
        .reset_index()
    )

    forecast_annual = forecast_annual[
        forecast_annual["year"] > last_year
    ].head(years)

    return forecast_annual, model, forecast, df


def plot_heating_oil_forecast(forecast_annual):
    """
    Grafica la predicción anual del heating oil.
    """

    plt.figure(figsize=(10, 5))

    plt.plot(
        forecast_annual["year"],
        forecast_annual["predicted_dollars_per_gallon"],
        marker="o",
        label="Predicción"
    )

    plt.fill_between(
        forecast_annual["year"],
        forecast_annual["lower_dollars_per_gallon"],
        forecast_annual["upper_dollars_per_gallon"],
        alpha=0.2,
        label="Intervalo de incertidumbre"
    )

    plt.title("Predicción precio anual Heating Oil - New York")
    plt.xlabel("Año")
    plt.ylabel("$/gallon")
    plt.grid(True)
    plt.legend()
    plt.show()


# %%
API_KEY = "8M0JstWWu6UqKUC20EcMouZruPmFDIit6C2OG5p8"

df_oil_pred, oil_model, oil_forecast_weekly, oil_historical_df = (
    forecast_annual_heating_oil_price(
        api_key=API_KEY,
        years=15
    )
)

print("Último dato histórico:")
print(oil_historical_df["ds"].max())

print("\nPredicción anual:")
print(df_oil_pred)

df_oil_pred.to_csv("oil_forecast.csv", index=False)

plot_heating_oil_forecast(df_oil_pred)

