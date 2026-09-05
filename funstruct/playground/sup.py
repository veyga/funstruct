# #!/usr/bin/env -S uv run --script
# # /// script
# # requires-python = ">=3.13"
# # dependencies = [
# # "debugpy",
# # "coloredlogs",
# # ]
# # ///
#
# import os, coloredlogs, logging
#
# if os.getenv("ENABLE_DEBUG"):
#     import debugpy
#
#     debugpy.listen(("0.0.0.0", 5680))
#     debugpy.wait_for_client()
#
# log = logging.getLogger("sup.py")
# coloredlogs.install(
#     level="DEBUG",
#     fmt="%(asctime)s %(name)s %(levelname)-8s %(message)s",
#     field_styles={"levelname": {"color": "cyan", "bold": False}},
# )
#
#
# def main():
#     log.debug("hello world")
#
#
# if __name__ == "__main__":
#     main()
