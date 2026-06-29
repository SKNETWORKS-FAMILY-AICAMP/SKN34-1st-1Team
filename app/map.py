import folium
import pandas as pd
from typing import Optional

_KATEC_TO_WGS84 = (
    "+proj=tmerc +lat_0=38 +lon_0=128 +k=0.9999 +x_0=400000 +y_0=600000 "
    "+ellps=bessel +units=m +towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43"
)


def katec_to_wgs84(x: float, y: float) -> tuple[float, float]:
    """Convert Opinet KATEC coordinates to WGS84 (lat, lon)."""
    from pyproj import Transformer

    transformer = Transformer.from_crs(_KATEC_TO_WGS84, "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(x, y)
    return lat, lon


def prepare_stations_for_map(stations: pd.DataFrame) -> pd.DataFrame:
    if stations.empty:
        return stations

    df = stations.copy()
    lat = (
        pd.to_numeric(df["latitude"], errors="coerce")
        if "latitude" in df.columns
        else pd.Series(float("nan"), index=df.index)
    )
    lon = (
        pd.to_numeric(df["longitude"], errors="coerce")
        if "longitude" in df.columns
        else pd.Series(float("nan"), index=df.index)
    )

    if "gis_x_coor" in df.columns and "gis_y_coor" in df.columns:
        gis_x = pd.to_numeric(df["gis_x_coor"], errors="coerce")
        gis_y = pd.to_numeric(df["gis_y_coor"], errors="coerce")
        missing = lat.isna() | lon.isna()
        for idx in df.index[missing]:
            x, y = gis_x.at[idx], gis_y.at[idx]
            if pd.notna(x) and pd.notna(y):
                lat.at[idx], lon.at[idx] = katec_to_wgs84(float(x), float(y))

    df["latitude"] = lat
    df["longitude"] = lon
    return df.dropna(subset=["latitude", "longitude"])


def _popup_html(row: pd.Series, price_column: str) -> str:
    name = row.get("station_name") or "주유소"
    price = _price_label(row, price_column)
    return f"<b>{name}</b><br>{price}"


def _price_label(row: pd.Series, price_column: str) -> str:
    price = row.get(price_column)
    if pd.notna(price):
        return f"{int(price):,}원"
    return "-"


_PIN_POINTER_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="14" height="10" viewBox="0 0 14 10">
  <path fill="{color}" d="M7 10 L0 0 L14 0 Z"/>
</svg>
"""


def _leaflet_pin_icon(station_name: str, price_label: str, color: str = "#dc2626") -> folium.DivIcon:
    import html

    name = html.escape(str(station_name or "주유소"))
    price = html.escape(str(price_label or "-"))
    label_html = (
        f'<div style="background:#fff;border:2px solid {color};border-radius:4px;'
        f'padding:3px 6px;font-size:10px;text-align:center;line-height:1.3;'
        f'max-width:120px;box-shadow:0 1px 3px rgba(0,0,0,.15);">'
        f'<div style="font-weight:700;color:#111;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
        f'{name}</div>'
        f'<div style="font-weight:700;color:{color};margin-top:1px;">{price}</div>'
        f'</div>'
    )

    pointer_svg = _PIN_POINTER_SVG.format(color=color).strip()
    html = f"""
    <div style="display:flex;flex-direction:column;align-items:center;line-height:1;">
      {label_html}
      <div style="margin-top:1px;line-height:0;">{pointer_svg}</div>
    </div>
    """

    return folium.DivIcon(
        html=html,
        icon_size=(130, 52),
        icon_anchor=(65, 52),
        popup_anchor=(0, -46),
        class_name="leaflet-pin-icon",
    )


def _rank_color(rank: int, total: int) -> str:
    """Cheapest (rank 1) = red, most expensive = yellow."""
    if total <= 1:
        return "#dc2626"

    ratio = (rank - 1) / (total - 1)
    red = (220, 38, 38)
    yellow = (234, 179, 8)
    r = int(red[0] + (yellow[0] - red[0]) * ratio)
    g = int(red[1] + (yellow[1] - red[1]) * ratio)
    b = int(red[2] + (yellow[2] - red[2]) * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"


def build_gas_stations_map(
    stations: pd.DataFrame,
    price_column: str = "gasoline_price",
) -> Optional[folium.Map]:
    mapped = prepare_stations_for_map(stations)
    if mapped.empty:
        return None

    center_lat = mapped["latitude"].mean()
    center_lon = mapped["longitude"].mean()

    folium_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles="CartoDB positron",
    )

    mapped = mapped.copy()
    mapped[price_column] = pd.to_numeric(mapped[price_column], errors="coerce")
    mapped["_price_rank"] = mapped[price_column].rank(method="min", ascending=True)
    total = len(mapped)

    for _, row in mapped.iterrows():
        name = row.get("station_name") or "주유소"
        rank = int(row["_price_rank"]) if pd.notna(row["_price_rank"]) else total
        color = _rank_color(rank, total)
        price = _price_label(row, price_column)
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            icon=_leaflet_pin_icon(name, price, color=color),
            tooltip=f"{name} · {price}",
            popup=folium.Popup(_popup_html(row, price_column), max_width=240),
        ).add_to(folium_map)

    if len(mapped) > 1:
        folium_map.fit_bounds(mapped[["latitude", "longitude"]].values.tolist())

    return folium_map
