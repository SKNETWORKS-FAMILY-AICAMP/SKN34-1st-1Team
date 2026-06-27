import pandas as pd


def month_start(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).dt.to_period("M").dt.to_timestamp()


def oil_car_dataset(oil_df: pd.DataFrame, car_df: pd.DataFrame) -> pd.DataFrame:
    if oil_df.empty or car_df.empty:
        return pd.DataFrame()

    oil = oil_df.copy()
    cars = car_df.copy()
    oil["month"] = month_start(oil["month"])
    cars["month"] = month_start(cars["month"])

    cars_agg = (
        cars.groupby(["month", "fuel_type"], as_index=False)
        .agg(units=("units", "sum"), avg_fuel_efficiency=("avg_fuel_efficiency", "mean"))
    )
    oil_agg = oil.groupby("month", as_index=False).agg(avg_price=("avg_price", "mean"))
    merged = cars_agg.merge(oil_agg, on="month", how="inner").sort_values("month")
    merged["oil_price_change_pct"] = merged["avg_price"].pct_change() * 100
    merged["sales_change_pct"] = merged.groupby("fuel_type")["units"].pct_change() * 100
    return merged


def oil_transit_dataset(oil_df: pd.DataFrame, transit_df: pd.DataFrame) -> pd.DataFrame:
    if oil_df.empty or transit_df.empty:
        return pd.DataFrame()

    oil = oil_df.copy()
    transit = transit_df.copy()
    oil["month"] = month_start(oil["month"])
    transit["month"] = month_start(transit["month"])

    oil_agg = oil.groupby("month", as_index=False).agg(avg_price=("avg_price", "mean"))
    transit_agg = (
        transit.groupby(["month", "transport_type"], as_index=False)
        .agg(rides=("rides", "sum"))
    )
    merged = transit_agg.merge(oil_agg, on="month", how="inner").sort_values("month")
    merged["oil_price_change_pct"] = merged["avg_price"].pct_change() * 100
    merged["rides_change_pct"] = merged.groupby("transport_type")["rides"].pct_change() * 100
    return merged
