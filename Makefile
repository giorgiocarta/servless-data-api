package:
	chalice package ./target/packaged

sdk:
	chalice generate-sdk ./target/sdk

deploy:
	chalice deploy