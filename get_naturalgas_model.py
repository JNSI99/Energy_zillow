
import requests
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet


def get_eia_monthly_natural_gas_prices_ny(
    api_key,
    area="SNY",
    process="PRS"
):
    """
    Descarga precios mensuales de gas natural desde EIA.

    Default:
        area="SNY"      -> New York
        process="PRS"   -> Price Delivered to Residential Consumers

    Retorna:
        DataFrame con columnas:
            ds = fecha mensual
            y  = precio en dollars per thousand cubic feet
    """

    url = "https://api.eia.gov/v2/natural-gas/pri/sum/data/"

    params = {
        "api_key": api_key,
        "frequency": "monthly",
        "data[]": "value",
        "facets[duoarea][]": area,
        "facets[process][]": process,
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": 5000,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()["response"]["data"]

    df = pd.DataFrame(data)

    df = df[["period", "value"]].copy()
    df["ds"] = pd.to_datetime(df["period"])
    df["y"] = pd.to_numeric(df["value"], errors="coerce")

    df = df[["ds", "y"]].dropna()
    df = df.sort_values("ds")

    return df


def forecast_annual_natural_gas_price(
    api_key,
    years=15,
    area="SNY",
    process="PRS"
):
    """
    Entrena Prophet con precios mensuales de gas natural
    y devuelve la predicción promedio anual para los próximos años.

    Retorna:
        forecast_annual
        model
        forecast_monthly
        historical_df
    """

    df = get_eia_monthly_natural_gas_prices_ny(
        api_key=api_key,
        area=area,
        process=process
    )

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.05
    )

    model.fit(df)

    future = model.make_future_dataframe(
        periods=years * 12,
        freq="MS"
    )

    forecast = model.predict(future)

    forecast_future = forecast[forecast["ds"] > df["ds"].max()].copy()
    forecast_future["year"] = forecast_future["ds"].dt.year

    forecast_annual = (
        forecast_future
        .groupby("year")
        .agg(
            predicted_dollars_per_mcf=("yhat", "mean"),
            lower_dollars_per_mcf=("yhat_lower", "mean"),
            upper_dollars_per_mcf=("yhat_upper", "mean"),
        )
        .reset_index()
        .head(years)
    )

    return forecast_annual, model, forecast, df


def plot_annual_natural_gas_forecast(forecast_annual):
    """
    Grafica la predicción anual del precio promedio de gas natural.
    """

    plt.figure(figsize=(10, 5))

    plt.plot(
        forecast_annual["year"],
        forecast_annual["predicted_dollars_per_mcf"],
        marker="o",
        label="Predicción"
    )

    plt.fill_between(
        forecast_annual["year"],
        forecast_annual["lower_dollars_per_mcf"],
        forecast_annual["upper_dollars_per_mcf"],
        alpha=0.2,
        label="Intervalo de incertidumbre"
    )

    plt.title("Predicción del precio promedio anual del gas natural en NY")
    plt.xlabel("Año")
    plt.ylabel("Precio promedio, $/Mcf")
    plt.grid(True)
    plt.legend()
    plt.show()

API_KEY = "8M0JstWWu6UqKUC20EcMouZruPmFDIit6C2OG5p8"

df_gas_pred, gas_model, gas_forecast_monthly, gas_historical_df = (
    forecast_annual_natural_gas_price(
        api_key=API_KEY,
        years=15
    )
)

print(df_gas_pred)

df_gas_pred.to_csv("gas_forecast.csv", index=False)

plot_annual_natural_gas_forecast(df_gas_pred)