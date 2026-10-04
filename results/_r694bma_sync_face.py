"""r694 bm-a: post-push sync_face settle (r474/r483 law: pool-carrying push ->
immediate lane/shared settle). merge_lane_views.sync_face is a library path
(no CLI subcommand) -- call it directly."""
import sys

sys.path.insert(0, "scripts")
import merge_lane_views as mlv

rc = mlv.sync_face("runnable_pool")
print("sync_face rc:", rc)
