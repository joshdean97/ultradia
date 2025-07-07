import boto3

client = boto3.client("ses", region_name="us-east-1")

response = client.send_email(
    Source="josh@ultradia.app",
    Destination={"ToAddresses": ["joshuashepherd877@gmail.com"]},
    Message={
        "Subject": {"Data": "UltraDia is Live 🚀"},
        "Body": {
            "Text": {"Data": "Test email from your SES setup. You're in rhythm now."}
        },
    },
)

print(response)
