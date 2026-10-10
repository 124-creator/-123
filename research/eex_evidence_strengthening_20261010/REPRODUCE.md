# Reproduction and scope

Work in a **new scratch copy** of this directory; do not run into the published outputs. No notebook/model deserialization is required.

1. Obtain the exact historical EEX input ZIP identified in `PROTOCOL_BEFORE_RUN.md` on GitHub (data commit5745eb3ddca79602346053446583d794b0e09800), with lawful use. This package does not redistribute it.
2. Extract it to a separate input directory. Keep the six workbooks and all parsed records together. `run_strengthening.py` checks the 11 input-manifest files, exact cells and eligibility before fitting.
3. With Python3.12+ and NumPy2.3.5/SciPy1.17.0, run:

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -B code/test_strengthening.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -O -B code/test_strengthening.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -B code/run_strengthening.py --inputs /path/to/extracted/input
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -B code/independent_crosscheck.py --inputs /path/to/extracted/input
```

Check `audit/EXECUTION_RECEIPT.json`, failed draws and balance results, not just the coefficient. The main estimator must not be tuned to make the auction-volume KS diagnostic pass.

For E3, obtain a lawfully retained 2026 workbook matching the source hash in `results/newtime_2026/NEW_TIME_RESULTS.json`. The dynamic public URL may have changed. The historical exact byte snapshot is **not** archived in this output package. Run `code/run_newtime_2026.py --input <exact_workbook> --out <new_output_dir>`. Do not call a different file the same replication or widen the Jan–Sep cutoff. This is new-time re-estimation, not a predictive evaluation.

The additional source file `assemble_results.py` combines existing output files; `write_report.py` generates manuscript insertion and Chinese report; `build_figures.py` draws completed values only. Figures are not additional tests. Excel is a presentation of the numerical outputs, not the fitting engine.

Before-run public protocol commit: 2151017871416fe0ad2505cfdbda23162aaa873e.
Pre-2026 acquisition arithmetic clarification: c308845659e91baa530404220e1e67c0b1ff2024.
Self-authored source publication: e9930cd2eea15164d4f7858d318f5c9c84e06cc1.

The method paper's code was not executed. Reference optimizers operate on this same archive, not independent market data. Historical exploration, SD-population uncertainty, temporal dependence and selected auction success remain part of the limitations.
