import subprocess
import os
import time

all_data = []

# PER values to simulate — add or change as needed
pers = [0.01, 0.05, 0.1, 0.2, 0.3, 0.5]

output_path = "results/output.txt"

if not os.path.exists("results"):
    os.makedirs("results")

for per in pers:
    print(f"\n--- Running Simulation PER: {per} ---")
    env = os.environ.copy()
    env["PER"] = str(per)

    # Bring down any previous stack cleanly first
    subprocess.run(
        ["docker", "compose", "down", "--remove-orphans"],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    cmd = ["docker", "compose", "up", "--build", "--exit-code-from", "sender"]
    process = subprocess.Popen(
        cmd, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True
    )

    found = False
    for line in process.stdout:
        print(line, end="", flush=True)
        if "FINAL_RESULT:" in line:
            data_part = line.split("FINAL_RESULT:")[1].strip()
            parts = data_part.split(":")
            if len(parts) == 2:
                per_val, thr_val = parts
                all_data.append(f"{per_val},{thr_val}")
                found = True

    process.wait()

    if not found:
        print(f"WARNING: No FINAL_RESULT found for PER={per}")

    # Tear down after each run
    subprocess.run(
        ["docker", "compose", "down", "--remove-orphans"],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

print("\n--- Saving Results ---")
with open(output_path, "w") as f:
    for entry in all_data:
        f.write(entry + "\n")

print(f"Saved '{output_path}' with {len(all_data)} data points.")
print("\nContents:")
for line in all_data:
    print(" ", line)
