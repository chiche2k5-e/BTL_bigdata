"""
Full Pipeline Runner: collect -> parse -> etl -> chunk -> index
Usage:
    python scripts/run_pipeline.py [--step all|collect|parse|etl|chunk|index]
"""
import argparse
import logging
import subprocess
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

PIPELINE_STEPS = ["collect", "parse", "etl", "chunk", "index"]


def run_step(step_name: str) -> bool:
    script_path = f"scripts/run_{step_name}.py"
    logger.info(f"============================================================")
    logger.info(f"▶️ RUNNING STEP: {step_name.upper()} ({script_path})")
    logger.info(f"============================================================")
    start_time = time.time()

    cmd = [sys.executable, script_path]
    try:
        result = subprocess.run(cmd, check=True)
        elapsed = time.time() - start_time
        logger.info(f"✅ Step {step_name.upper()} finished in {elapsed:.2f}s")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Step {step_name.upper()} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error in step {step_name.upper()}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run the end-to-end Data Lake + RAG pipeline")
    parser.add_argument("--step", default="all", choices=["all"] + PIPELINE_STEPS,
                        help="Specific pipeline step to run, or 'all'")
    args = parser.parse_args()

    steps_to_run = PIPELINE_STEPS if args.step == "all" else [args.step]

    total_start = time.time()
    for step in steps_to_run:
        success = run_step(step)
        if not success:
            logger.error(f"💥 Pipeline aborted at step '{step}'. Fix the issue and resume.")
            sys.exit(1)

    total_elapsed = time.time() - total_start
    logger.info(f"🎉 Pipeline finished successfully in {total_elapsed:.2f}s!")


if __name__ == "__main__":
    main()
