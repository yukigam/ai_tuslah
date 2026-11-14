"""Discover OCI compartments, subnets, and images to fill in sniper placeholders."""
import oci

config = oci.config.from_file()
config["region"] = "ap-tokyo-1"
tenancy_id = config["tenancy"]

identity = oci.identity.IdentityClient(config)
compute = oci.core.ComputeClient(config)
network = oci.core.VirtualNetworkClient(config)

print("=" * 70)
print("1. COMPARTMENTS (active)")
print("=" * 70)
compartments = oci.pagination.list_call_get_all_results(
    identity.list_compartments,
    compartment_id=tenancy_id,
    compartment_id_in_subtree=True,
    access_level="ANY",
).data
for c in compartments:
    if c.lifecycle_state == "ACTIVE":
        print(f"  Name: {c.name}")
        print(f"  OCID: {c.id}")
        print()

print("=" * 70)
print("2. AVAILABILITY DOMAINS")
print("=" * 70)
ads = identity.list_availability_domains(compartment_id=tenancy_id).data
for ad in ads:
    print(f"  Name: {ad.name} | OCID: {ad.id}")
print()

print("=" * 70)
print("3. VCNs and SUBNETS (per active compartment)")
print("=" * 70)
for comp in compartments:
    if comp.lifecycle_state != "ACTIVE":
        continue
    try:
        vcns = network.list_vcns(compartment_id=comp.id).data
        for vcn in vcns:
            subnets = network.list_subnets(compartment_id=comp.id, vcn_id=vcn.id).data
            for subnet in subnets:
                print(f"  Compartment: {comp.name}")
                print(f"  VCN: {vcn.display_name} ({vcn.id})")
                print(f"  Subnet: {subnet.display_name} | OCID: {subnet.id} | AD: {subnet.availability_domain}")
                print()
    except Exception as e:
        print(f"  Skipping compartment {comp.name}: {e}")
        print()

print("=" * 70)
print("4. IMAGES (per active compartment)")
print("=" * 70)
for comp in compartments:
    if comp.lifecycle_state != "ACTIVE":
        continue
    try:
        images = oci.pagination.list_call_get_all_results(
            compute.list_images,
            compartment_id=comp.id,
            operating_system="Oracle Linux",
        ).data
        for img in images[:10]:  # limit to first 10 per compartment
            print(f"  Compartment: {comp.name}")
            print(f"  Image: {img.display_name} | OCID: {img.id} | OS: {img.operating_system} {img.operating_system_version}")
            print()
    except Exception as e:
        print(f"  Skipping compartment {comp.name}: {e}")
        print()

print("Done. Copy the OCIDs you need into oci_sniper.py.")
