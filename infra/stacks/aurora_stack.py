import os

from aws_cdk import (
    # aws_dynamodb as dynamodb,
    aws_iam as iam,
    core as cdk,
    aws_secretsmanager as sm,
    aws_ec2 as ec2,
    aws_rds as rds
)
from cdk_chalice import Chalice

# from aws_cdk import aws_ec2 as ec2
# from aws_cdk import aws_rds as rds
from aws_cdk import aws_lambda as lambda_
from aws_cdk import core

class AuroraDbStack(cdk.Stack):

    def __init__(self, scope: core.Construct, id: str, props: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        db_root_username = props.get('DB_ROOT_USERNAME')
        db_root_password = props.get('DB_ROOT_PASSWORD')
        vpc = props.get('vpc')
        db_name = props.get('DB_NAME')
        

        # secret = rds.DatabaseSecret(
        #     self,
        #     id="DbRootUserSecret",
        #     username=db_master_user_name
        # )


        subnet_group = rds.CfnDBSubnetGroup(
            self,
            id="AuroraServerlessSubnetGroup",
            db_subnet_group_description='Aurora Postgres Serverless Subnet Group',
            subnet_ids=list(map(lambda x :x.subnet_id, vpc.isolated_subnets)),
            db_subnet_group_name='auroraserverlesssubnetgroup'  # needs to be all lowercase
        )

        db_cluster_name = "aurora-serverless-postgres-db"

        security_group = ec2.SecurityGroup(
            self,
            id="SecurityGroup",
            vpc=vpc,
            description="Allow ssh access to ec2 instances",
            allow_all_outbound=True
        )
        security_group.add_ingress_rule(ec2.Peer.ipv4(
            '10.0.0.0/16'), ec2.Port.tcp(5432), "allow psql through")

        self.db = rds.CfnDBCluster(
            self,
            id="AuroraServerlessDB",
            engine=rds.DatabaseClusterEngine.AURORA_POSTGRESQL.name,
            engine_mode="serverless",
            db_subnet_group_name=subnet_group.db_subnet_group_name,

            vpc_security_group_ids=[security_group.security_group_id],
            availability_zones=vpc.availability_zones,

            db_cluster_identifier=db_cluster_name,
            # db_cluster_parameter_group_name=

            database_name=db_name,
            master_username= db_root_username,
            # secret.secret_value_from_json("username").to_string(),
            master_user_password=db_root_password,
            # secret.secret_value_from_json("password").to_string(),

            port=5432,

            deletion_protection=False,
            scaling_configuration=rds.CfnDBCluster.ScalingConfigurationProperty(
                auto_pause=True,
                min_capacity=2,
                max_capacity=8,
                seconds_until_auto_pause=300
            ),

            # enable_cloudwatch_logs_exports=[
            #     "error",
            #     "general",
            #     "slowquery",
            #     "audit"
            # ],
            enable_http_endpoint=True
            # kms_key_id=
            # tags=
        )


        #secret_attached = secret.attach(target=self)
        #secret.add_target_attachment(id="secret_attachment", target=self.db)

        # secret_attached = sm.CfnSecretTargetAttachment(
        #     self,
        #     id="secret_attachment",
        #     secret_id=secret.secret_arn,
        #     target_id=self.db.ref,
        #     target_type="AWS::RDS::DBCluster",
        # )
        # secret_attached.node.add_dependency(self.db)

        core.CfnOutput(
            self,
            id="DatabaseName",
            value=self.db.database_name,
            description="Database Name",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:database-name"
        )

        core.CfnOutput(
            self,
            id="DatabaseClusterID",
            value=self.db.db_cluster_identifier,
            description="Database Cluster Id",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:database-cluster-id"
        )

        core.CfnOutput(
            self,
            id="AuroraEndpointAddress",
            value=self.db.attr_endpoint_address,
            description="Aurora Endpoint Address",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:aurora-endpoint-address"
        )

        core.CfnOutput(
            self,
            id="DatabaseMasterUserName",
            value=db_root_username,
            description="Database Master User Name",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:database-master-username"
        )


class WebApi(cdk.Stack):

    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, 'VPC', vpc_name="my_vpc")

        # lambda_sg = kwargs.pop('lambda_sg', None)

        lambda_service_principal = iam.ServicePrincipal('lambda.amazonaws.com')
        self.api_handler_iam_role = iam.Role(self, 'ApiHandlerLambdaRole',
                                             assumed_by=lambda_service_principal)

        self.dynamodb_table.grant_read_write_data(self.api_handler_iam_role)

        data_api_source_dir = os.path.join(os.path.dirname(__file__), os.pardir,
                                           os.pardir, 'data-api')

        chalice_stage_config = self._create_chalice_stage_config()
        self.chalice = Chalice(
            self, 'DataAPI', source_dir=data_api_source_dir,
            stage_config=chalice_stage_config)


#  {
#   "version": "2.0",
#   "app_name": "data-api",
#   "stages": {
#     "dev": {
#       "api_gateway_stage": "api",
#       "environment_variables": {
#         "TEST" : "Giorgio"
#       }
#     }
#   }
# }

    def _create_chalice_stage_config(self):
        chalice_stage_config = {
            'api_gateway_stage': 'v1',
            'lambda_functions': {
                'api_handler': {
                    'manage_iam_role': False,
                    'iam_role_arn': self.api_handler_iam_role.role_arn,
                    'environment_variables': {
                        'DYNAMODB_TABLE_NAME': self.dynamodb_table.table_name,
                        'AURORA_CLUSTER_ARN': 'A',
                        'AURORA_SECRET_ARN': 'B',
                        'AURORA_DATABASE_NAME': 'C',
                        'TEST': "Giorgio"
                    },
                    'lambda_memory_size': 128,
                    'lambda_timeout': 10
                }
            }
        }

        chalice_stage_config_1 = {
            "version": "2.0",
            "app_name": "data-api",
            "stages": {
                "dev": {
                        "api_gateway_stage": "api",
                        "environment_variables":
                            {
                                'DYNAMODB_TABLE_NAME': self.dynamodb_table.table_name,
                                'AURORA_CLUSTER_ARN': 'A',
                                'AURORA_SECRET_ARN': 'B',
                                'AURORA_DATABASE_NAME': 'C',
                                'TEST': "Giorgio"
                            },
                        # "security_group_ids" : [].append(self)

                }
            }
        }
        return chalice_stage_config


class DataProcessingRTStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, 'VPC', vpc_name="my_vpc")

        lambda_sg = kwargs.pop('lambda_sg', None)

        with open("lambda-handler.py", encoding="utf8") as fp:
            handler_code = fp.read()

        lambda_fn = lambda_.Function(
            self, "DB_Lambda",
            code=lambda_.InlineCode(handler_code),
            handler="index.main",
            timeout=core.Duration.seconds(300),
            runtime=lambda_.Runtime.PYTHON_3_7,
            security_group=lambda_sg,
        )

        aurora_sg = ec2.SecurityGroup(
            self, 'AUPG-SG',
            vpc=vpc,
            description="Allows PosgreSQL connections from Lambda SG",
        )
        aurora_cluster = rds.DatabaseCluster(
            self, "AUPG-CLUSTER-1",
            engine=rds.DatabaseClusterEngine.AURORA_POSTGRESQL,
            engine_version="10.7",
            master_user=rds.Login(
                username='admin',
                password=core.SecretValue.ssm_secure(
                    'AUPG.AdminPass', version='1'),
            ),
            default_database_name='MyDatabase',
            instance_props=rds.InstanceProps(
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.MEMORY5, ec2.InstanceSize.XLARGE,
                ),
                vpc=vpc,
                security_group=aurora_sg,
            ),
            parameter_group=rds.ClusterParameterGroup.from_parameter_group_name(
                self, "AUPG-ParamGroup-1",
                parameter_group_name="default.aurora-postgresql10",
            )
        )

        connectors_sg = ''
        aurora_cluster.connections.allow_from(
            connectors_sg, ec2.Port.tcp(3306),
            "Allow MySQL access from Lambda (because Aurora actually exposes PostgreSQL on port 3306)"
        )
