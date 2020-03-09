
# requires jq
jq --version foo >/dev/null 2>&1 || { echo >&2 "I require JQ but it's not installed.  Aborting."; exit 1; }

# get Public IP from stack output
PUBLIC_IP=`aws --profile giorgio2 cloudformation describe-stacks --stack-name custom-vpc-staging | jq '.Stacks[0].Outputs[2].OutputValue'`

# remove leading and trailing double quote
PUBLIC_IP="${PUBLIC_IP%\"}"
PUBLIC_IP="${PUBLIC_IP#\"}"

echo "Connecting to "$PUBLIC_IP
ssh -i ssh-bastion.pem ec2-user@$PUBLIC_IP

# tunnel first
ssh -N -i "ssh-bastion.pem" \
    -L "localhost:5432:postgres-staging.cnspxqqbefin.eu-west-1.rds.amazonaws.com:5432" \
    ec2-user@PUBLIC_IP

# connect easy
psql -h postgres-staging.cnspxqqbefin.eu-west-1.rds.amazonaws.com:5432 -U test -d mydb
