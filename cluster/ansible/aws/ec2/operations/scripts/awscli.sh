#!/bin/bash
#--------------------------------------------------------------------------------
# Run the ansible playbook to stop instances.
# See https://c-scope.atlassian.net/wiki/display/CC/DevOps+-+CC+-+2.0+-+Environment+-+AWS+-+Instance+Management
#--------------------------------------------------------------------------------
set -eu

DIR=$(dirname $(realpath $0))
. ${DIR}/_utility.sh


aws ec2 create-snapshot-volume-id vol-0919aca5c3d55b222 --description "qa-ubuntu:/"
aws ec2 create-tags --resources snap-0445acbe858f9fff2 --tags Key=Name,Value=qa-ubuntu:/
aws ec2 describe-snapshots --snapshot-id snap-0857aaaab538dca6e

aws --region us-east-2 ec2 copy-snapshot --source-region us-east-1 --source-snapshot-id snap-02a344cb4e8f33a52 --description "This is my copied snapshot."

aws --region us-east-2 ec2 describe-volumes --volume-ids vol-0f67c39f4f875f7b4

aws --region us-east-2 ec2 describe-volume-status --volume-ids vol-0f67c39f4f875f7b4

snapshots_to_delete=($(aws --region us-east-1 ec2 describe-snapshots --owner-ids 752398066937 --query 'Snapshots[?StartTime< `2017-07-25`].SnapshotId' --output text))
echo "List of snapshots to delete: $snapshots_to_delete"

# actual deletion
for snap in $snapshots_to_delete; do
    echo $snap
done
