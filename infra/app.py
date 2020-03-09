#!/usr/bin/env python3

from infra.stacks.vpc_stack import VPCStack
from infra.stacks.aurora_stack import AuroraDbStack
from os import environ
from aws_cdk import core
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# from infra.stacks.aurora_stack import DataProcessingRTStack, WebApi

env_EU = core.Environment(
    account=environ.get("CDK_DEPLOY_ACCOUNT",
                        environ["CDK_DEFAULT_ACCOUNT"]),
    region=environ.get("CDK_DEPLOY_REGION",
                       environ["CDK_DEFAULT_REGION"])
)


props = {}
props['BASTION_EC2_TYPE'] = environ.get('BASTION_EC2_TYPE')
props['SECRET_KEY_NAME'] = environ.get('SECRET_KEY_NAME')
props['DB_ROOT_USERNAME'] = environ.get('DB_ROOT_USERNAME')
props['DB_ROOT_PASSWORD'] = environ.get('DB_ROOT_PASSWORD')
props['DB_NAME'] = environ.get('DB_NAME')
app = core.App()

vpc_ec2_stack = VPCStack(
    scope=app,
    id="VPC",
    env=env_EU,
    props=props
)

db_stack = AuroraDbStack(
    scope=app,
    id="AuroraDbStack",
    env=env_EU,
    props=vpc_ec2_stack.output_props
)

app.synth()

# DataProcessingRTStack(app, "infra")
# WebApi(app, "infra")

# app.synth()
