#!/usr/bin/env python3
"""EJOR validation protocol — config-driven, staged, reproducible.

Single-command reproduction:
    python run_protocol.py --config configs/ejor_pilot.yaml --stage all
Stage-by-stage (recommended in constrained environments):
    python run_protocol.py --config configs/ejor_pilot.yaml --stage benchmark
    ... redundancy | probes | gates | direct | stochastic | multistakeholder | report

Outputs -> ../results/protocol/{tables,figures}. Acceptance gates are summarised
in gates_report.{csv,json}.
"""
import argparse, json, os, sys, time
import numpy as np, pandas as pd, yaml
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lur import problems, methods, families, stats as st, gates, directopt, extras_validation
from lur.methods import normalize

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "protocol"))
TAB = f"{ROOT}/tables"; FIG = f"{ROOT}/figures"


_MCW = [1000]   # Monte-Carlo weight count for randomized methods (set per run)


def _select(name, F, rng):
    fn = methods.METHODS[name]
    if name in methods.RANDOMIZED:
        if name == "RW":
            return fn(F, rng=rng, n_weights=min(_MCW[0], 200))
        return fn(F, rng=rng, n_weights=_MCW[0])
    return fn(F)


def _load_json(p, d=None):
    try:
        return json.load(open(p))
    except Exception:
        return {} if d is None else d


def _save_json(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w"), indent=2, default=float)


TMP = f"{ROOT}/tmp_v2"       # benchmark chunk store (bounded-generator full run)


# --------------------------------------------------------------------------- #
def _bench_block(cfg, csizes, crits):
    """Run the benchmark over the given candidate sizes and criteria, returning
    paired (inst x M) matrices of tail/mean/worst-family loss. Deterministic:
    the per-instance seed depends only on (csize, m, geometry-index, rep), so
    chunked runs concatenate to exactly the same suite as a single full run."""
    geoms_all = cfg["geometries"]
    sel = cfg.get("_geoms")
    geoms = [(gi, g) for gi, g in enumerate(geoms_all) if (sel is None or g in sel)]
    reps = cfg["replications"]
    nU = cfg["utilities_per_family"]; alphas = cfg["dirichlet_alphas"]
    fam = cfg["families"]; M = cfg["methods"]; tailq = cfg["tail_q"]
    base = cfg["seed"]
    Pt, Pm, Pw = [], [], []
    for N in csizes:
        for m in crits:
            for gi, g in geoms:
                for rep in range(reps):
                    a = alphas[rep % len(alphas)]
                    s = (base * 1009 + N * 131 + m * 17 + gi * 7 + rep) & 0x7fffffff
                    rr = np.random.default_rng(s)
                    F = problems.make_candidate_set(g, N, m, rr)
                    cache = families.loss_cache(F, normalize, np.random.default_rng(s + 1),
                                                alpha=a, n_per_family=nU, family_list=fam)
                    selrng = np.random.default_rng(s + 2)
                    rt, rm, rw = [], [], []
                    for nm in M:
                        idx = _select(nm, F, rng=selrng)
                        ml, tl, wf, _ = families.losses_from(cache, idx, q=tailq)
                        rt.append(tl); rm.append(ml); rw.append(wf)
                    Pt.append(rt); Pm.append(rm); Pw.append(rw)
    return np.array(Pt), np.array(Pm), np.array(Pw)


def stage_benchmark(cfg):
    """Run one chunk (restricted by --csize/--crit) and persist it, OR, with no
    restriction, run the whole suite in-memory and finalise."""
    M = cfg["methods"]
    csizes = [cfg["_csize"]] if cfg.get("_csize") else cfg["candidate_sizes"]
    crits = cfg["_crit"] if cfg.get("_crit") else cfg["criteria"]
    Pt, Pm, Pw = _bench_block(cfg, csizes, crits)
    if cfg.get("_csize") or cfg.get("_crit") or cfg.get("_geoms"):   # chunk mode
        os.makedirs(TMP, exist_ok=True)
        cs = csizes[0] if cfg.get("_csize") else "all"
        gtag = "-".join(g[:3] for g in cfg["_geoms"]) if cfg.get("_geoms") else "allg"
        tag = f"{cs}_{'-'.join(map(str,crits))}_{gtag}"
        np.savez(f"{TMP}/bench_{tag}.npz", Pt=Pt, Pm=Pm, Pw=Pw, methods=np.array(M))
        print(f"  saved chunk {tag}: {Pt.shape[0]} instances")
        return
    _benchmark_finalize_from(cfg, Pt, Pm, Pw)


def stage_bfinalize(cfg):
    """Concatenate all persisted benchmark chunks and compute final stats."""
    import glob
    M = cfg["methods"]
    files = sorted(glob.glob(f"{TMP}/bench_*.npz"))
    if not files:
        raise SystemExit("no benchmark chunks found in tmp/")
    Pt = np.vstack([np.load(f)["Pt"] for f in files])
    Pm = np.vstack([np.load(f)["Pm"] for f in files])
    Pw = np.vstack([np.load(f)["Pw"] for f in files])
    print(f"  combined {len(files)} chunks -> {Pt.shape[0]} instances")
    _benchmark_finalize_from(cfg, Pt, Pm, Pw)


def _benchmark_finalize_from(cfg, Pt, Pm, Pw):
    M = cfg["methods"]
    df = pd.DataFrame([dict(method=nm, mean_loss=Pm[:, j].mean(),
                            tail_loss=Pt[:, j].mean(), worst_family=Pw[:, j].mean())
                       for j, nm in enumerate(M)])
    os.makedirs(TAB, exist_ok=True)
    df.to_csv(f"{TAB}/benchmark.csv", index=False)
    P = Pt
    fried = st.friedman(P); ranks = st.average_ranks(P)
    cd = st.nemenyi_cd(len(M), P.shape[0])
    wh = st.wilcoxon_holm(P, M, control="LUR")
    # non-inferiority vs ASF and MMR
    li = M.index("LUR")
    noninf = {}
    for ctrl in ["ASF", "MMR"]:
        noninf[ctrl] = gates.noninferiority(P[:, li], P[:, M.index(ctrl)],
                                            margin=cfg["noninferiority_margin"], name=ctrl)
    summary = dict(n_instances=int(P.shape[0]), friedman=fried, cd=cd,
                   avg_ranks={nm: float(r) for nm, r in zip(M, ranks)},
                   wilcoxon_vs_LUR={k: dict(p_raw=v[0], p_holm=v[1], delta=v[2])
                                    for k, v in wh.items()},
                   noninferiority=noninf)
    _save_json(f"{TAB}/benchmark_stats.json", summary)
    # CD figure
    order = np.argsort(ranks); names = [M[i] for i in order]; rr = ranks[order]
    fig, ax = plt.subplots(figsize=(9, 2.6)); ax.axis("off")
    ax.hlines(0.75, 1, len(M), color="k")
    for nm, v in zip(names, rr):
        ax.vlines(v, 0.7, 0.8); ax.text(v, 0.6, f"{nm}\n{v:.2f}", ha="center", va="top", fontsize=7)
    ax.plot([1, 1 + cd], [0.92, 0.92], lw=3, color="crimson")
    ax.text(1 + cd / 2, 0.96, f"CD={cd:.2f}", ha="center", color="crimson", fontsize=8)
    ax.set_ylim(0, 1); ax.set_xlim(0.5, len(M) + 0.5)
    ax.set_title("Average ranks — tail held-out loss (protocol suite)", fontsize=9)
    os.makedirs(FIG, exist_ok=True); fig.tight_layout()
    fig.savefig(f"{FIG}/cd_protocol.pdf"); plt.close(fig)
    print(f"  instances={P.shape[0]} LUR tail rank={summary['avg_ranks']['LUR']:.2f} "
          f"NI(ASF)={noninf['ASF']['noninferior']} NI(MMR)={noninf['MMR']['noninferior']}")
    return summary


def stage_redundancy(cfg):
    rc = cfg["redundancy"]; rng = np.random.default_rng(cfg["seed"] + 1)
    M = cfg["methods"]; nU = cfg["utilities_per_family"]; fam = cfg["families"]
    agg = {m_: {"grp": [], "tail": []} for m_ in M}
    cluster_recovery = []
    for c in rc["latent"]:
        for struct in rc["structures"]:
            if len(struct) != c:
                struct = (struct * c)[:c]
            for _ in range(rc["replications"]):
                g = problems.GEOMETRIES[int(rng.integers(0, 4))]
                F, groups, base = problems.make_redundant_set(g, 300, struct, rng)
                # cluster recovery: adjusted agreement of discovered vs true groups
                cl = methods.correlation_clusters(F, cfg["theta"])
                lab = np.zeros(F.shape[1], int)
                for k, comp in enumerate(cl):
                    for j in comp:
                        lab[j] = k
                cluster_recovery.append(_cluster_match(lab, groups))
                cb = families.loss_cache(base, normalize, np.random.default_rng(int(rng.integers(1<<31))),
                                         n_per_family=nU, family_list=fam)
                cf = families.loss_cache(F, normalize, np.random.default_rng(int(rng.integers(1<<31))),
                                         n_per_family=nU, family_list=fam)
                selrng = np.random.default_rng(int(rng.integers(1 << 31)))
                for nm in M:
                    idx = _select(nm, F, rng=selrng)
                    agg[nm]["grp"].append(families.losses_from(cb, idx)[0])
                    agg[nm]["tail"].append(families.losses_from(cf, idx)[1])
    df = pd.DataFrame([dict(method=nm, grouped_loss=np.mean(agg[nm]["grp"]),
                            tail_loss=np.mean(agg[nm]["tail"])) for nm in M])
    os.makedirs(TAB, exist_ok=True); df.to_csv(f"{TAB}/redundancy.csv", index=False)
    _save_json(f"{TAB}/redundancy_extra.json",
               dict(mean_cluster_recovery=float(np.mean(cluster_recovery))))
    print(f"  cluster recovery={np.mean(cluster_recovery):.3f}; "
          f"LUR grp={df.set_index('method').loc['LUR','grouped_loss']:.3f}")
    return df


def _cluster_match(lab, truth):
    """fraction of criterion pairs whose same/different-group status agrees."""
    m = len(lab); agree = tot = 0
    for i in range(m):
        for j in range(i + 1, m):
            agree += int((lab[i] == lab[j]) == (truth[i] == truth[j])); tot += 1
    return agree / tot if tot else 1.0


def stage_probes(cfg):
    rng = np.random.default_rng(cfg["seed"] + 2)
    nU = cfg["utilities_per_family"]; fam = cfg["families"]
    variants = ["adaptive", "full", "singletons", "no_singletons", "max_only",
                "cluster_only", "random"]
    rows = {v: {"tail": [], "agree_full": [], "nprobes": []} for v in variants}
    for m in [3, 5, 8]:                          # full family only tractable for small m
        for _ in range(20):
            F = problems.make_candidate_set("concave", 300, m, rng)
            cache = families.loss_cache(F, normalize, np.random.default_rng(int(rng.integers(1<<31))),
                                        n_per_family=nU, family_list=fam)
            i_full = methods.lur_variant(F, "full")
            for v in variants:
                iv = methods.lur_variant(F, v, rng=np.random.default_rng(1))
                rows[v]["tail"].append(families.losses_from(cache, iv)[1])
                rows[v]["agree_full"].append(float(iv == i_full))
    df = pd.DataFrame([dict(variant=v, tail_loss=np.mean(rows[v]["tail"]),
                            agree_with_full=np.mean(rows[v]["agree_full"])) for v in variants])
    os.makedirs(TAB, exist_ok=True); df.to_csv(f"{TAB}/probes.csv", index=False)
    print(df.to_string(index=False))
    return df


def stage_gates(cfg):
    g = cfg["gates"]
    res = {}
    res["dominated"] = gates.gate_dominated_injection(g["dominated_injection"])
    res["affine"] = gates.gate_affine_invariance(tests=g["affine_tests"])
    res["nadir"] = gates.gate_nadir_error(g["nadir_errors"])
    _save_json(f"{TAB}/gates_invariance.json", res)
    print(f"  dominated pass={res['dominated']['pass']} "
          f"affine={res['affine']['identical_rate']} nadir_pass={res['nadir']['pass']}")
    return res


def stage_direct(cfg):
    lin = directopt.run_linear_case(m=4, reps=10)
    mil = directopt.run_facility_location()
    out = dict(linear=lin, milp=mil)
    _save_json(f"{TAB}/direct.json", out)
    print("  linear:", {k: round(v, 3) for k, v in lin.items()})
    print("  milp:", mil)
    return out


def stage_stochastic(cfg):
    sc = cfg["stochastic"]
    df = extras_validation.run_stochastic(train_scenarios=sc["train_scenarios"],
                                          test_scenarios=sc["test_scenarios"],
                                          alphas=tuple(sc["alphas"]))
    os.makedirs(TAB, exist_ok=True); df.to_csv(f"{TAB}/stochastic.csv", index=False)
    print(df.to_string(index=False))
    return df


def stage_multistakeholder(cfg):
    df = extras_validation.run_multistakeholder(stakeholders=tuple(cfg["multistakeholder"]["stakeholders"]))
    os.makedirs(TAB, exist_ok=True); df.to_csv(f"{TAB}/multistakeholder.csv", index=False)
    print(df.groupby("method")[["worst_regret", "mean_regret", "gini"]].mean().to_string())
    return df


def stage_report(cfg):
    """Assemble the acceptance-gate table from persisted stage outputs."""
    bs = _load_json(f"{TAB}/benchmark_stats.json")
    gi = _load_json(f"{TAB}/gates_invariance.json")
    rows = []

    def add(gate, passed, detail):
        rows.append(dict(gate=gate, result="PASS" if passed else "CHECK", detail=detail))

    if gi:
        d = gi["dominated"]; add("Dominated selections = 0",
            d["pass"], f"{d['violations']}/{d['trials']} violations")
        a = gi["affine"]; add("Positive-affine invariance",
            a["pass"], f"identical rate {a['identical_rate']}")
        nd = gi["nadir"]; add("Nadir-error stability",
            nd["pass"], f"max quality degradation {nd['max_quality_degradation']}")
    if bs:
        ni = bs["noninferiority"]
        add("Tail non-inferiority vs ASF", ni["ASF"]["noninferior"],
            f"diff {ni['ASF']['mean_diff']} CI {ni['ASF']['ci95']}")
        add("Tail non-inferiority vs MMR", ni["MMR"]["noninferior"],
            f"diff {ni['MMR']['mean_diff']} CI {ni['MMR']['ci95']}")
        wh = bs["wilcoxon_vs_LUR"]
        practical = ["TOPSIS", "CP", "Knee", "RW", "SMAA"]
        beat = all(wh[p]["p_holm"] < 0.05 and wh[p]["delta"] > 0 for p in practical if p in wh)
        add("Better than practical baselines (tail)", beat,
            "; ".join(f"{p}:d={wh[p]['delta']:+.2f}" for p in practical if p in wh))
    # redundancy
    try:
        rd = pd.read_csv(f"{TAB}/redundancy.csv").set_index("method")
        avg = rd.loc[["TOPSIS", "SMAA", "RW"], "grouped_loss"].mean()
        add("Redundancy: LUR < averaging (grouped)", rd.loc["LUR", "grouped_loss"] < avg,
            f"LUR {rd.loc['LUR','grouped_loss']:.3f} vs avg {avg:.3f}")
    except Exception:
        pass
    # probes adaptive vs full
    try:
        pr = pd.read_csv(f"{TAB}/probes.csv").set_index("variant")
        gap = pr.loc["adaptive", "tail_loss"] - pr.loc["full", "tail_loss"]
        add("Adaptive probes ~ full (tail gap <= 0.01)", abs(gap) <= 0.01,
            f"gap {gap:+.4f}, agree {pr.loc['adaptive','agree_with_full']:.2f}")
    except Exception:
        pass
    # direct
    try:
        dr = _load_json(f"{TAB}/direct.json")
        lin = dr["linear"]
        add("Direct computation demonstrated (LP+MILP)",
            dr.get("milp", {}).get("available", False),
            f"LP direct calls {lin['direct_calls']:.0f} vs enum {lin['enum_calls']:.0f}")
    except Exception:
        pass
    # stochastic
    try:
        sd = pd.read_csv(f"{TAB}/stochastic.csv").set_index("method")
        best_alpha = sd.filter(like="LUR-a", axis=0)["tail_loss"].min()
        add("Stochastic LUR <= deterministic LUR (tail)",
            best_alpha <= sd.loc["det-LUR", "tail_loss"] + 1e-9,
            f"best-alpha {best_alpha:.3f} vs det {sd.loc['det-LUR','tail_loss']:.3f}")
    except Exception:
        pass
    rep = pd.DataFrame(rows)
    rep.to_csv(f"{TAB}/gates_report.csv", index=False)
    _save_json(f"{TAB}/gates_report.json", rows)
    print(rep.to_string(index=False))
    return rep


STAGES = {"benchmark": stage_benchmark, "bfinalize": stage_bfinalize,
          "redundancy": stage_redundancy,
          "probes": stage_probes, "gates": stage_gates, "direct": stage_direct,
          "stochastic": stage_stochastic, "multistakeholder": stage_multistakeholder,
          "report": stage_report}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/ejor_pilot.yaml")
    ap.add_argument("--stage", default="all", choices=list(STAGES) + ["all"])
    ap.add_argument("--csize", type=int, default=None,
                    help="restrict benchmark to one candidate size (chunked run)")
    ap.add_argument("--crit", default=None,
                    help="comma list of criteria counts to restrict the benchmark chunk")
    ap.add_argument("--utils", type=int, default=None,
                    help="override utilities_per_family (for time-constrained runs)")
    ap.add_argument("--mcw", type=int, default=None,
                    help="Monte-Carlo weight count for randomized methods")
    ap.add_argument("--geoms", default=None,
                    help="comma list of geometries to restrict the benchmark chunk")
    args = ap.parse_args()
    if args.mcw:
        _MCW[0] = args.mcw
    cfg = yaml.safe_load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           args.config)))
    cfg["_csize"] = args.csize
    cfg["_crit"] = [int(x) for x in args.crit.split(",")] if args.crit else None
    cfg["_geoms"] = [x.strip() for x in args.geoms.split(",")] if args.geoms else None
    if args.utils:
        cfg["utilities_per_family"] = args.utils
    os.makedirs(TAB, exist_ok=True); os.makedirs(FIG, exist_ok=True)
    # 'all' should not silently chunk-skip finalisation
    todo = [s for s in STAGES if s != "bfinalize"] if args.stage == "all" else [args.stage]
    for s in todo:
        t0 = time.time(); print(f"[protocol stage: {s}]", flush=True)
        STAGES[s](cfg); print(f"  ...{time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
