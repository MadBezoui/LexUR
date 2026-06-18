REQUIRED_BENCHMARK_COLUMNS = {
    "run_id", "config_sha256", "seed", "N", "m", "geometry",
    "replication", "dirichlet_alpha", "method", "utility_scope",
    "mean_loss", "tail_loss", "worst_family", "selected_index",
}


def expected_benchmark_cells(cfg: dict) -> int:
    return (
        len(cfg["candidate_sizes"])
        * len(cfg["criteria"])
        * len(cfg["geometries"])
        * int(cfg["replications"])
    )


def validate_benchmark_frame(frame, cfg: dict) -> None:
    missing = REQUIRED_BENCHMARK_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"missing benchmark columns: {sorted(missing)}")
    cells = frame[["N", "m", "geometry", "replication"]].drop_duplicates()
    expected = expected_benchmark_cells(cfg)
    if len(cells) != expected:
        raise ValueError(f"expected {expected} benchmark cells, found {len(cells)}")
