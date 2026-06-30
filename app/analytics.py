import pandas as pd

PRODUCT_LABELS = {
    "normal_gasoline": "휘발유",
    "diesel": "경유",
}


def month_start(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).dt.to_period("M").dt.to_timestamp()


def prepare_gas_sales(gas_df: pd.DataFrame) -> pd.DataFrame:
    if gas_df.empty:
        return pd.DataFrame()

    gas = gas_df.copy()
    gas["month"] = month_start(gas["month"])
    long = gas.melt(
        id_vars=["month"],
        value_vars=["normal_gasoline", "diesel"],
        var_name="product_key",
        value_name="avg_price",
    )
    long["product"] = long["product_key"].map(PRODUCT_LABELS)
    return long.sort_values("month")


def gas_sales_table(gas_df: pd.DataFrame) -> pd.DataFrame:
    if gas_df.empty:
        return pd.DataFrame()

    gas = gas_df.copy()
    gas["month"] = month_start(gas["month"])
    gas = gas.sort_values("month", ascending=True)
    return gas


def prepare_transit_usage(transit_df: pd.DataFrame) -> pd.DataFrame:
    if transit_df.empty:
        return pd.DataFrame()

    transit = transit_df.copy()
    transit.columns = [str(col).strip() for col in transit.columns]
    transit["month"] = month_start(transit["month"])
    return transit.sort_values("month", ascending=True)


def gas_car_dataset(gas_df: pd.DataFrame, car_df: pd.DataFrame) -> pd.DataFrame:
    if gas_df.empty or car_df.empty:
        return pd.DataFrame()

    gas = gas_df.copy()
    cars = car_df.copy()
    gas["month"] = month_start(gas["month"])
    cars["month"] = month_start(cars["month"])
    gas["avg_price"] = (gas["normal_gasoline"] + gas["diesel"]) / 2

    cars_agg = (
        cars.groupby(["month", "fuel_type"], as_index=False)
        .agg(units=("units", "sum"), avg_fuel_efficiency=("avg_fuel_efficiency", "mean"))
    )
    gas_agg = gas.groupby("month", as_index=False).agg(avg_price=("avg_price", "mean"))
    merged = cars_agg.merge(gas_agg, on="month", how="inner").sort_values("month")
    merged["price_change_pct"] = merged["avg_price"].pct_change() * 100
    merged["sales_change_pct"] = merged.groupby("fuel_type")["units"].pct_change() * 100
    return merged


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
