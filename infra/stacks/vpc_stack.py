from os import path

from aws_cdk import (
    aws_ec2 as ec2,
    core
)

current_path = path.dirname(path.realpath(__file__))

with open(path.join(current_path, "config.sh")) as f:
    bastion_user_data = f.read()

class VPCStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, props: dict,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        public_subnet = ec2.SubnetConfiguration(
            name="public-subnet",
            subnet_type=ec2.SubnetType.PUBLIC,
            cidr_mask=24,
            reserved=False,
        )

        private_subnet_a = ec2.SubnetConfiguration(
            name="private-subnet-a",
            subnet_type=ec2.SubnetType.ISOLATED,
            cidr_mask=24,
            reserved=False,
        )

        # print(dir(private_subnet_a.subnet))

        # private_subnet_b = ec2.SubnetConfiguration(
        #     name="private-subnet-b",
        #     subnet_type=ec2.SubnetType.ISOLATED,
        #     cidr_mask=24,
        #     reserved=False,
        # )

        subnets = [public_subnet, private_subnet_a]

        vpc = ec2.Vpc(
            self,
            id="DatabaseVPC",
            cidr="10.0.0.0/16",
            max_azs=3,
            nat_gateways=0,
            subnet_configuration=subnets,
            enable_dns_hostnames=True,
            enable_dns_support=True
        )

        # vpc.isolated_subnets[0].instance.add_property_override('availability_zone','eu-west-a')
        # vpc.isolated_subnets[1].instance.add_property_override('availability_zone','eu-west-b')
        


        # setup a bastion host
        # this lives in the public subnet
        # and allows ssh connections to the private subnets
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2.README.html#bastion-hosts
        bastion = ec2.BastionHostLinux(
            self,
            id="PublicBastionHost",
            vpc=vpc,
            instance_name="PublicBastionHost",
            instance_type=ec2.InstanceType(props.get('BASTION_EC2_TYPE')),
            subnet_selection=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            )
        )
        bastion.instance.user_data.add_commands(bastion_user_data)

        # asset = Asset(self, "Asset", path=path.join(__dirname, "configure.sh"))

        # restrict access to ssh port
        bastion.allow_ssh_access_from(ec2.Peer.any_ipv4())

        # set access using this secret key
        bastion.instance.instance.add_property_override("KeyName", props.get('SECRET_KEY_NAME'))


        # -------- outputs -------- #
        # Prints vpc id
        core.CfnOutput(
            self, 
            id="VcpId",
            description="The Virtual Private Cloud ID",
            value=vpc.vpc_id
        )


        core.CfnOutput(
            self,
            id="BastionPrivateIP",
            value=bastion.instance_private_ip,
            description="The bastion Private IP",
        )

        core.CfnOutput(
            self,
            id="BastionPublicIP",
            value=bastion.instance_public_ip,
            description="The Bastion Public IP"
        )


        # pass on some values
        self.output_props=props.copy()
        self.output_props['vpc']=vpc
        self.output_props['public_subnet']=public_subnet
        self.output_props['private_subnet_a']=private_subnet_a
        # self.output_props['private_subnet_b']=private_subnet_b
        self.output_props['bastion']=bastion

    @property
    def outputs(self) -> dict:
        """
        pass topic to other stack
        """
        return self.output_props
