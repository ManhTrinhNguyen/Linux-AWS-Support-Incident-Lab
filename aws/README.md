# Optional AWS extension

Finish the local exercises first. This creates real billable resources. It is optional
and has not been deployed by the repository authoring session. No AWS resources are
created by the Docker quick start or GitHub workflow.

## What this adds
One dedicated VPC, public subnet, route, internet gateway, security group,
Amazon Linux 2023 EC2 instance, instance role, and private S3 bucket with two sample objects.
No EKS, NAT gateway, or load balancer. Only SSH from your /32 is allowed inbound.
EC2, EBS, public IPv4, and S3 may incur charges; do not assume free-tier eligibility.

## Before you begin
- Install Terraform >=1.6 and AWS CLI v2 on your workstation.
- Use a sandbox AWS account with permission to create the listed resources.
- Authenticate with your normal AWS profile or SSO. Do not put credentials in this repo.
- Create an EC2 key pair in your chosen region; keep the private key outside this repo.
- Find your current public IPv4 using your router or a trusted IP-check service.

From the repository root:
```bash
cd aws
cp terraform.tfvars.example terraform.tfvars
# EDIT terraform.tfvars: region, your real public IPv4/32, and key pair name.
aws sts get-caller-identity
terraform init
terraform fmt
terraform validate
terraform plan -out=lab.tfplan
# Review the resources and costs before executing:
terraform apply lab.tfplan
terraform output
```
Never upload state, plans, tfvars, keys, or unredacted command output.
Commit the generated .terraform.lock.hcl after your own successful init.

## Connect and install the lab
Use your output IP instead of PUBLIC_IP and your actual private-key path:
```bash
chmod 400 /path/to/your-key.pem
ssh -i /path/to/your-key.pem ec2-user@PUBLIC_IP
sudo cloud-init status --wait
sudo docker info
```
If installation failed, inspect `/var/log/cloud-init-output.log`.
Install Docker Compose on the instance following the official plugin instructions:
https://docs.docker.com/compose/install/linux/#install-the-plugin-manually
Use the architecture appropriate to the instance (this configuration uses x86_64).
Verify `sudo docker compose version`. Do not assume Docker's package includes Compose.

After publishing your repository, clone YOUR URL on EC2:
```bash
git clone https://github.com/YOUR_USERNAME/linux-aws-support-incident-lab.git
cd linux-aws-support-incident-lab
sudo bash scripts/lab.sh start
```
On your workstation, in a second terminal:
```bash
ssh -i /path/to/your-key.pem -N -L 18080:127.0.0.1:8080 ec2-user@PUBLIC_IP
```
Visit http://127.0.0.1:18080/health. Port 8080 stays closed to public traffic.
Run the local scenarios on EC2 with `sudo bash scripts/lab.sh ...`.

## AWS incident A: new SSH connections time out
Do this only on the lab's security group. Keep the AWS console open.
1. Confirm a NEW SSH connection succeeds. Record the exact port-22 rule and /32.
2. In EC2 > Security Groups, remove that port-22 ingress rule from the lab group.
3. Try a NEW SSH connection with `ssh -o ConnectTimeout=5 ...`; existing sessions
   can remain active because security groups track connections.
4. Check instance status, public IP, attached security group, and inbound rule.
5. Restore the exact SSH rule through the AWS console using your current /32.
6. Verify a NEW connection works. Do not solve this by opening SSH to everyone.
7. Record evidence in a copy of the ticket template. Describe it as a simulated
   security-group incident, not a production outage.

## AWS incident B: S3 AccessDenied
Run these on EC2 using its attached role. Do not configure a different AWS profile there.
Replace BUCKET_NAME with Terraform's bucket output:
```bash
aws sts get-caller-identity
aws s3api get-object --bucket BUCKET_NAME --key allowed/example.txt /tmp/allowed.txt
aws s3api get-object --bucket BUCKET_NAME --key restricted/example.txt /tmp/restricted.txt
```
If AWS CLI is absent, install CLI v2 using the official AWS instructions linked below.
The first object should succeed, the restricted object should return AccessDenied.
If both initially fail, allow a short time for IAM propagation and verify the identity.
Inspect the inline role policy: it only allows GetObject under `allowed/*`.
This is an intentional policy boundary, not an outage. First establish whether access
is actually authorized. If a simulated customer needs the approved example, correct
the requested key to `allowed/example.txt`. If access to the restricted object is
approved for the exercise, update ONLY that object's ARN in Terraform's policy,
review the plan, apply, and retry. Do not grant s3:* or attach AdministratorAccess.
Do not use bucket listing as a health check: ListBucket is intentionally not granted.

## Native Linux service exercise
Follow [native-linux.md](../docs/native-linux.md) on this disposable EC2 host.
This exercises systemctl and journalctl beyond container commands.

## Clean up
On your WORKSTATION from aws/:
```bash
terraform plan -destroy
terraform destroy
```
Keep state until cleanup succeeds. Added S3 objects can prevent bucket deletion;
remove only extra objects you created in this lab bucket, then retry. Confirm the
instance, bucket, and other managed resources are gone in the console. The EC2 key
pair you supplied is not managed or deleted by this configuration.

## Official references
- AWS CLI install: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- Security groups: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules-reference.html
- IAM evaluation: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html
- Terraform AWS provider: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
