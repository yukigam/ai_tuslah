"""
OCI Automated Instance Sniper
=============================

Continuously attempts to launch a VM.Standard.A1.Flex instance in OCI region
ap-tokyo-1 (Availability Domain AD-1) until capacity becomes available.

Placeholders to replace before running:
    COMPARTMENT_ID  -> your compartment OCID
    SUBNET_ID       -> your subnet OCID
    IMAGE_ID        -> your image OCID
"""

import oci
import time
from datetime import datetime

# ==================== USER CONFIGURATION ====================
COMPARTMENT_ID = "ocid1.tenancy.oc1..aaaaaaaao6f2mi5pxmg7yqma4jlh322fxt57t7rr6dy2upabzs7uoory5tha"
SUBNET_ID = "ocid1.subnet.oc1.ap-tokyo-1.aaaaaaaabn223shdnimzyzwinixubdcdqum77nukr5d3757nkds3hid5gp2a"
IMAGE_ID = "ocid1.image.oc1.ap-tokyo-1.aaaaaaaawufbvqj6xzjrvr2f7uyhvgr7ejyzyqu4fcx72omwqimsvqymh7na"

REGION = "ap-tokyo-1"
AVAILABILITY_DOMAIN = "fhOL:AP-TOKYO-1-AD-1"
SHAPE = "VM.Standard.A1.Flex"
OCPUS = 1
MEMORY_IN_GBS = 6
INSTANCE_DISPLAY_NAME = "oci-sniper-instance"
BOOT_VOLUME_SIZE_IN_GBS = 50
POLL_INTERVAL_SECONDS = 30
# ============================================================


def log(message):
    """Print a timestamped status message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def resolve_ad_ocid(identity_client, tenancy_id, ad_name):
    """Look up the full Availability Domain OCID by its display name."""
    ads = identity_client.list_availability_domains(
        compartment_id=tenancy_id
    ).data
    for ad in ads:
        if ad.name == ad_name:
            return ad.id
    return None


def main():
    # Load OCI config from the default location (~/.oci/config)
    config = oci.config.from_file()
    config["region"] = REGION

    tenancy_id = config["tenancy"]
    compute_client = oci.core.ComputeClient(config)
    identity_client = oci.identity.IdentityClient(config)

    log(f"Starting OCI instance sniper in region {REGION}")
    log(f"Target shape: {SHAPE} | OCPUs={OCPUS} | Memory={MEMORY_IN_GBS} GB")
    log(f"Availability Domain: {AVAILABILITY_DOMAIN}")
    log(f"Compartment: {COMPARTMENT_ID}")
    log("Press Ctrl+C to stop.\n")

    # Resolve the Availability Domain OCID
    ad_ocid = resolve_ad_ocid(identity_client, tenancy_id, AVAILABILITY_DOMAIN)
    if not ad_ocid:
        log(f"ERROR: Availability Domain '{AVAILABILITY_DOMAIN}' not found in tenancy.")
        return
    log(f"Resolved AD OCID: {ad_ocid}\n")

    attempt = 0
    while True:
        attempt += 1
        try:
            launch_details = oci.core.models.LaunchInstanceDetails(
                availability_domain=ad_ocid,
                compartment_id=COMPARTMENT_ID,
                display_name=INSTANCE_DISPLAY_NAME,
                shape=SHAPE,
                shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
                    ocpus=OCPUS,
                    memory_in_gbs=MEMORY_IN_GBS,
                ),
                subnet_id=SUBNET_ID,
                source_details=oci.core.models.InstanceSourceViaImageDetails(
                    image_id=IMAGE_ID,
                    boot_volume_size_in_gbs=BOOT_VOLUME_SIZE_IN_GBS,
                ),
            )

            response = compute_client.launch_instance(launch_details)
            log(
                "SUCCESS! Instance launched: "
                f"id={response.data.id}, display_name={response.data.display_name}"
            )
            break

        except oci.exceptions.ServiceError as e:
            error_msg = str(e)
            is_capacity_issue = (
                "Out of capacity" in error_msg
                or "TooManyRequests" in error_msg
                or e.status == 429
                or e.status == 400
            )
            if is_capacity_issue:
                log(
                    f"Attempt {attempt}: Capacity unavailable or throttled "
                    f"(HTTP {e.status}). Retrying in {POLL_INTERVAL_SECONDS}s..."
                )
            else:
                log(
                    f"Attempt {attempt}: Unexpected OCI ServiceError: {error_msg}"
                )
            time.sleep(POLL_INTERVAL_SECONDS)

        except Exception as e:
            log(f"Attempt {attempt}: Unexpected error: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
