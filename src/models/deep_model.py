"""Global N-BEATS forecasting via Darts for M5 leaf-level series."""
import numpy as np
import pandas as pd


def make_timeseries(long_df, series_ids, id_col="id", time_col="date",
                    value_col="sales"):
    """Convert selected series in a long frame to a list of Darts TimeSeries."""
    from darts import TimeSeries
    series_list = []
    kept_ids = []
    for sid in series_ids:
        g = long_df[long_df[id_col] == sid].sort_values(time_col)
        if len(g) < 60:          # need enough history
            continue
        ts = TimeSeries.from_dataframe(
            g, time_col=time_col, value_cols=value_col, freq="D"
        )
        series_list.append(ts)
        kept_ids.append(sid)
    return series_list, kept_ids


def build_nbeats(input_chunk=56, output_chunk=28, quantiles=(0.1, 0.5, 0.9)):
    from darts.models import NBEATSModel
    from darts.utils.likelihood_models import QuantileRegression
    model = NBEATSModel(
        input_chunk_length=input_chunk,
        output_chunk_length=output_chunk,
        num_stacks=10, num_blocks=1, num_layers=4,
        layer_widths=256,
        n_epochs=15, batch_size=512,
        likelihood=QuantileRegression(quantiles=list(quantiles)),
        random_state=42,
        pl_trainer_kwargs={"accelerator": "gpu", "devices": 1,
                           "enable_progress_bar": True},
    )
    return model
