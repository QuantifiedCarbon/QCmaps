"""Provides plotting functionalities."""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap
from QCmaps.io import get_gdf, process_gdf, georeference


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
    #    colorempty = "gainsboro"
    colorempty = "whitesmoke"
    #    colorempty = "floralwhite"
    #    colormap = "coolwarm"
    #    colormap = "bluered"
    colormap = "QC"
    if colormap == "bluered":
        cmap = plt.get_cmap("coolwarm")
        cmap = LinearSegmentedColormap.from_list(
            "bluered", [cmap.get_under(), cmap.get_over()]
        )
    if colormap == "QC":
        #        color_QC_background = [0.184, 0.267, 0.314, 1]
        #        color_QC_logo = [0.859, 0.988, 0.557, 1]
        color_blue = [0.2298057, 0.29871797, 0.75368315, 1.0]
        color_orange = [0.99215686, 0.55294118, 0.23529412, 1.0]
        color_red = [0.70567316, 0.01555616, 0.15023281, 1.0]

        colors = [
            #            color_QC_background,
            color_blue,
            #            color_QC_logo,
            color_orange,
            color_red,
        ]
        cmap = LinearSegmentedColormap.from_list("QCcmap", colors)
    else:
        cmap = plt.get_cmap(colormap)

    fc = {}
    fc["zones"] = gdf.iloc[:, 1:].dropna(how="all").index
    fc["results"] = gdf.iloc[:, 1:].columns
    fc["number_rows"] = 1
    fc["number_columns"] = len(fc["results"])
    fc["vmin"] = gdf.loc[fc["zones"]].iloc[:, 1:].min().min()
    fc["vmax"] = gdf.loc[fc["zones"]].iloc[:, 1:].max().max()
    fc["cempty"] = colorempty
    fc["cmap"] = cmap
    fc["norm"] = mcolors.Normalize(vmin=fc["vmin"], vmax=fc["vmax"])
    fc["sm"] = cm.ScalarMappable(cmap=fc["cmap"], norm=fc["norm"])

    figsize = (2.5 * fc["number_columns"], 4)

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
    gdf = gdf[gdf.is_valid]
    result = gdf.columns[1]
    zones = gdf.iloc[:, 1:].dropna(how="all").index
    minx, miny, maxx, maxy = gdf.loc[zones].total_bounds  # Bounding box for all three
    buffer = 0.05 * (
        maxx - minx
    )  # Optional: Add a small buffer for better visualization
    #    clip_area = [minx - buffer, maxx + buffer, miny - buffer, maxy + buffer]
    gdf.plot(ax=ax, color=fc["cempty"], linewidth=0.5, edgecolor="black")
    gdf.loc[zones].plot(
        ax=ax,
        column=result,
        cmap=fc["cmap"],
        linewidth=0.5,
        edgecolor="black",
        vmin=fc["vmin"],
        vmax=fc["vmax"],
    )
    for zone in zones:
        centroid = gdf.loc[zone].geometry.centroid
        ax.text(centroid.x, centroid.y, zone, ha="center", color="black", weight="bold")
    ax.set_title(result)
    ax.set_xlim(minx - buffer, maxx + buffer)
    ax.set_ylim(miny - buffer, maxy + buffer)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
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
    # gdf = georeference(gdf, "orthographic")
    fc = get_figconfig(gdf)
    fc["legend"] = legend_label
    fig = plot_figure(fc, gdf)

    #    fig.savefig("output.png", format="png", dpi=300, bbox_inches="tight")
    #    fig.savefig("output.svg", format="svg", dpi=300, bbox_inches="tight")

    return fig
