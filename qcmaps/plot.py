"""Provides plotting functionalities."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap
import QCcolours
from qcmaps.io import get_gdf, process_gdf, georeference, clip_geometry

COLORMAP = "QC_sequential"
# COLORMAP = "QC_diverging"
HIGHLIGHT_ZONES = "all"
BUFFER_FRAME = [-0.05, -0.05, 0.05, 0.05]
SHIFT_FRAME = [0, 0]


def get_figconfig(gdf):
    """
    Get figure configurations for plot.

    Parameters
    ----------
    gdf: gpd.GeoDataFrame
        Processed Geodataframe.

    Returns
    -------
    dict
        fc, Dictionary with figure configurations.
    """
    dpi = 300.0
    font_family = "Helvetica"
    #    font_family = "DejaVu Sans" # does not work when saving
    #    font_family = "Arial"
    font_size = 10
    #    colorempty = "whitesmoke"
    colorempty = "gainsboro"
    #    colorempty = "floralwhite"
    #    colorempty = "lightgray"
    #    colorhide = QCcolours.colours.QC_PLOT_FILL_COLOURS["QC_sand"]
    colorhide = "gainsboro"
    if COLORMAP == "QC_test":
        color_blue = [0.2298057, 0.29871797, 0.75368315, 1.0]
        color_orange = [0.99215686, 0.55294118, 0.23529412, 1.0]
        color_red = [0.70567316, 0.01555616, 0.15023281, 1.0]
        colors = [
            color_blue,
            color_orange,
            color_red,
        ]
        cmap = LinearSegmentedColormap.from_list("QCcmap", colors)
    if COLORMAP.startswith("QC_"):
        if COLORMAP.startswith("QC_sequential"):
            colors = QCcolours.QC_CMAP_COLOURS
        elif COLORMAP.startswith("QC_diverging"):
            colors = ["QC_green", "QC_blue", "QC_brown"]
        cmap = QCcolours.matplotlib_utils.make_cmap_range(colors)
        if COLORMAP.endswith("_r"):
            cmap = cmap.reversed()
    else:
        cmap = plt.get_cmap(COLORMAP)

    zones = gdf.iloc[:, 1:].dropna(how="all").index
    results = gdf.iloc[:, 1:].columns
    number_rows = 1
    number_columns = len(results)
    vmin = gdf.loc[zones].iloc[:, 1:].min().min()
    vmax = gdf.loc[zones].iloc[:, 1:].max().max()
    if COLORMAP.startswith("QC_diverging"):
        vamm = max(abs(vmax), abs(vmin))
        vmax = vamm
        vmin = -vamm
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    figsize = (2.5 * number_columns, 4)

    if HIGHLIGHT_ZONES == "all":
        highlight_zones = zones
    else:
        highlight_zones = HIGHLIGHT_ZONES

    fc = {}
    fc["zones"] = zones
    fc["results"] = results
    fc["number_rows"] = number_rows
    fc["number_columns"] = number_columns
    fc["vmin"] = vmin
    fc["vmax"] = vmax
    fc["cempty"] = colorempty
    fc["chide"] = colorhide
    fc["cmap"] = cmap
    fc["norm"] = norm
    fc["sm"] = sm
    fc["highlight_zones"] = highlight_zones
    fc["buffer_frame"] = BUFFER_FRAME
    fc["shift_frame"] = SHIFT_FRAME

    plt.rcParams.update(
        {
            "figure.dpi": dpi,
            "figure.frameon": False,
            "figure.figsize": figsize,
            "font.family": font_family,
            "axes.labelsize": font_size,  # color bar label
            "axes.titlesize": font_size,  # ax title label
            #        'figure.labelsize': font_size,
            #        'figure.titlesize': font_size,
            "font.size": font_size - 5,  # text in figure
            #        'legend.fontsize': font_size,
            #        'legend.title_fontsize': font_size,
            #        'xtick.labelsize': font_size,
            "ytick.labelsize": font_size,  # color bar numbers
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "pdf.use14corefonts": False,
        }
    )

    return fc


def get_area_frame(fc, gdf):
    """
    Get area frame to display plot.

    Parameters
    ----------
    fc: dict
        Figure configurations.

    gdf: gpd.GeoDataFrame
        Processed Geodataframe.

    Returns
    -------
    np.array
        area_frame, Area frame coordinates.
    """
    highlight_zones = fc["highlight_zones"]
    area_frame = gdf.loc[highlight_zones].total_bounds
    minx, miny, maxx, maxy = area_frame
    dx = maxx - minx
    dy = maxy - miny
    buffer_frame = np.array(fc["buffer_frame"])
    buffer_frame = buffer_frame * [dx, dy, dx, dy]
    area_frame = area_frame + buffer_frame
    shift_frame = np.array(2 * fc["shift_frame"])
    shift_frame = shift_frame * [dx, dy, dx, dy]
    area_frame = area_frame + shift_frame
    minx, miny, maxx, maxy = area_frame
    return area_frame


def get_subplot(ax, fc, gdf):
    """
    Get subplot parts of figure.

    Parameters
    ----------
    ax: matplotlib.axes._axes.Axes
        Figure ax.
    fc: dict
        Dictionary with figure configurations.
    gdf: gpd.GeoDataFrame
        Processed Geodataframe.

    Returns
    -------
    matplotlib.axes._axes.Axes
        ax, Figure ax.
    """
    result = gdf.columns[1]
    zones = gdf.iloc[:, 1:].dropna(how="all").index
    highlight_zones = fc["highlight_zones"]
    minx, miny, maxx, maxy = fc["area_frame"]

    gdf.plot(ax=ax, color=fc["cempty"], linewidth=0.5, edgecolor="white")
    gdf.loc[zones].plot(
        ax=ax,
        color=fc["chide"],
        linewidth=0.5,
        edgecolor="black",
    )
    gdf.loc[highlight_zones].plot(
        ax=ax,
        column=result,
        cmap=fc["cmap"],
        linewidth=0.5,
        edgecolor="black",
        vmin=fc["vmin"],
        vmax=fc["vmax"],
    )
    text_linewidth = 1
    for zone in highlight_zones:
        centroid = gdf.loc[zone].geometry.centroid
        value = gdf.loc[[zone]]
        value = value.iloc[:, 1].values.round(1)[0]
        face_text = f"{zone}\n{value}"
        ax.text(
            centroid.x,
            centroid.y,
            face_text,
            ha="center",
            va="center",
            color="black",
            weight="bold",
            path_effects=[
                path_effects.Stroke(linewidth=text_linewidth, foreground="white"),
                path_effects.Normal(),
            ],
        )

    ax.set_title(result)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    return ax


def add_cbar_legend(fig, fc):
    """
    Add color bar to figure.

    Parameters
    ----------
    fig: matplotlib.figure.Figure
        Figure.
    fc: dict
        Dictionary with figure configurations.
    """
    fig.subplots_adjust(right=0.85)
    cbar_ax = fig.add_axes([0.88, 0.15, 0.03, 0.7])
    cbar = fig.colorbar(fc["sm"], cax=cbar_ax)
    cbar.set_label(fc["legend"])


def plot_figure(fc, gdf):
    """
    Plot map figure.

    Parameters
    ----------
    fc: dict
        Dictionary with figure configurations.
    gdf: gpd.GeoDataFrame
        Processed Geodataframe.

    Returns
    -------
    matplotlib.figure.Figure
        fig, Figure.
    """
    fig, ax = plt.subplots(fc["number_rows"], fc["number_columns"])
    if fc["number_columns"] == 1:
        ax = get_subplot(ax, fc, gdf)
    else:
        ax = ax.flatten()
        for i, result in enumerate(fc["results"]):
            ax[i] = get_subplot(ax[i], fc, gdf[["geometry", result]])
    add_cbar_legend(fig, fc)
    plt.show()
    return fig


def plot(df, legend_label=""):
    """
    Get geometries, process and plot map figure.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe with parameter values.
    legend_label: str
        Legend label with unit.

    Returns
    -------
    matplotlib.figure.Figure
        fig, Figure.
    """
    gdf = get_gdf()
    gdf = process_gdf(df, gdf)
    gdf = georeference(gdf)
    fc = get_figconfig(gdf)
    fc["legend"] = legend_label
    fc["area_frame"] = get_area_frame(fc, gdf)
    if HIGHLIGHT_ZONES != "all":
        gdf = clip_geometry(fc, gdf)
    fig = plot_figure(fc, gdf)
    return fig
