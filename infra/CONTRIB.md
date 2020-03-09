# How this folder was setup


These are the steps I follwed when creating this folder.

```
mkdir infra
cd infra
cdk init --language python --generate-only
rm -rf infra
rm setup.py
rm source.bat
pip install 
mkdir stacks
pip install cdk-chalice
pip install pip install aws_cdk.core
pip freeze | grep 'cdk-chalice\|aws-cdk.core' > requirements.txt
mkdir stacks
touch stacks/__init__.py
touch stacks/aurora.py
```