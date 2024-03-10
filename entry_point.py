import base64
import os
import shutil
import subprocess
import time


def entry_point(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    if "data" in event:
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        print(pubsub_message)

    if os.path.exists('klastro'):
        shutil.rmtree('klastro')

    p = subprocess.Popen("git clone https://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@github.com/ebour/klastro",
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    for line in p.stdout.readlines():
        print(line)
    retval = p.wait()
    if retval == 0:
        max_duration = 60
        actual_duration = 0
        while not os.path.exists('klastro') or max_duration < actual_duration:
            time.sleep(1)
            actual_duration += 1
        if not os.path.exists('klastro'):
            raise Exception('Unable to git clone pull klastro repository.')

        p = subprocess.Popen("./klastro/update_feed.sh",
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        retval = p.wait()
    else:
        raise Exception('Unable to git clone pull klastro repository.')

if __name__ == "__main__":
    entry_point({}, None)
