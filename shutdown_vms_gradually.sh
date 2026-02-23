#!/bin/bash

# Configuration
PROJECT="infnet-kafka-classes-test"
ZONE="us-central1-a"
VMS=("kafka-broker-4" "kafka-broker-3" "kafka-broker-2" "kafka-broker-1")

echo "Starting gradual suspension of Kafka brokers..."

for VM in "${VMS[@]}"; do
    echo "----------------------------------------------------"
    
    # Check current status first
    STATUS=$(gcloud compute instances describe "$VM" --zone="$ZONE" --project="$PROJECT" --format='value(status)')
    if [ "$STATUS" == "TERMINATED" ] || [ "$STATUS" == "SUSPENDED" ]; then
        echo "$VM is already $STATUS. Skipping..."
        continue
    fi

    echo "Initiating suspension for $VM..."
    
    # Start the suspend command (using --async to monitor timeout in this script)
    gcloud compute instances suspend "$VM" --zone="$ZONE" --project="$PROJECT" --async --quiet
    
    START_TIME=$(date +%s)
    TIMEOUT=300 # 5 minutes

    # Wait until the status is SUSPENDED or TERMINATED
    echo "Waiting for $VM to reach SUSPENDED/TERMINATED status (Timeout: 5m)..."
    while true; do
        STATUS=$(gcloud compute instances describe "$VM" --zone="$ZONE" --project="$PROJECT" --format='value(status)')
        CURRENT_TIME=$(date +%s)
        ELAPSED=$((CURRENT_TIME - START_TIME))

        if [ "$STATUS" == "SUSPENDED" ] || [ "$STATUS" == "TERMINATED" ]; then
            echo "$VM is now $STATUS."
            break
        fi

        if [ $ELAPSED -ge $TIMEOUT ]; then
            echo "Suspension for $VM taking too long ($ELAPSED seconds). Forcing termination (stop)..."
            gcloud compute instances stop "$VM" --zone="$ZONE" --project="$PROJECT" --quiet
            # Reset timeout or just keep waiting for TERMINATED
            # To avoid multiple stop calls, we can set a flag or just let it loop
            TIMEOUT=999999 
        fi

        echo "Status of $VM: $STATUS ($ELAPSED/300s)"
        sleep 10
    done
done

echo "----------------------------------------------------"
echo "Operation completed successfully."
