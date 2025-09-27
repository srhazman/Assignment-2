import os
import csv
import subprocess
import matplotlib.pyplot as plt

TRACES = [
    "traces/bzip.trace",
    "traces/gcc.trace",
    "traces/sixpack.trace",
    "traces/swim.trace",
]
ALGS = ["rand", "lru", "clock"]
FRAMES = [2, 4, 8, 16, 32, 64, 128]

def run_memsim(trace, frames, alg):
    out = subprocess.check_output(
        ["python3", "memsim.py", trace, str(frames), alg, "quiet"],
        text=True,
    )
    res = {"trace": os.path.basename(trace), "alg": alg, "frames": frames}
    for ln in out.strip().splitlines():
        ln = ln.strip()
        if   ln.startswith("events in trace:"):      res["events"] = int(ln.split(":")[1])
        elif ln.startswith("total disk reads:"):     res["reads"]  = int(ln.split(":")[1])
        elif ln.startswith("total disk writes:"):    res["writes"] = int(ln.split(":")[1])
        elif ln.startswith("page fault rate:"):      res["rate"]   = float(ln.split(":")[1])
    res["faults_est"] = round(res["rate"] * res["events"])
    return res

def main():
    csv_rows = []
    csv_path = "vm_results.csv"

    for trace in TRACES:
        results = {alg: [] for alg in ALGS}
        for alg in ALGS:
            for f in FRAMES:
                r = run_memsim(trace, f, alg)
                results[alg].append(r)
                csv_rows.append({
                    "trace": r["trace"],
                    "algorithm": r["alg"],
                    "frames": r["frames"],
                    "events": r["events"],
                    "page_fault_rate": f"{r['rate']:.6f}",
                    "page_faults_est": r["faults_est"],
                    "disk_reads": r["reads"],
                    "disk_writes": r["writes"],
                })

        # make 3 plots without labels
        fig, axs = plt.subplots(3, 1, figsize=(9, 12), sharex=True)
        title = f"Trace: {os.path.basename(trace)}"
        axs[0].set_title(title)

        # 1) Page fault rate
        for alg in ALGS:
            y = [r["rate"] for r in results[alg]]
            axs[0].plot(FRAMES, y, marker="o", label=alg.upper())
        axs[0].set_ylabel("Page Fault Rate")
        axs[0].grid(True)
        axs[0].legend()

        # 2) Disk reads
        for alg in ALGS:
            y = [r["reads"] for r in results[alg]]
            axs[1].plot(FRAMES, y, marker="s", label=alg.upper())
        axs[1].set_ylabel("Disk Reads")
        axs[1].grid(True)

        # 3) Disk writes
        for alg in ALGS:
            y = [r["writes"] for r in results[alg]]
            axs[2].plot(FRAMES, y, marker="^", label=alg.upper())
        axs[2].set_ylabel("Disk Writes")
        axs[2].set_xlabel("Number of Frames")
        axs[2].grid(True)

        plt.tight_layout()
        out_png = f"{os.path.splitext(os.path.basename(trace))[0]}_clean.png"
        plt.savefig(out_png, dpi=220)
        plt.close()
        print(f"[saved] {out_png}")

    # write CSV of all results
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "trace","algorithm","frames","events",
            "page_fault_rate","page_faults_est","disk_reads","disk_writes"
        ])
        w.writeheader()
        w.writerows(csv_rows)
    print(f"[saved] {csv_path}")

if __name__ == "__main__":
    main()
