import requests
import boto3
import os
from dotenv import load_dotenv

if os.getenv("FLASK_ENV") == "development":
    load_dotenv()


def health_check(url="http://localhost:5000/api/health"):
    """
    Perform a health check on the given URL.

    Args:
        url (str): The URL to check.

    Returns:
        dict: A dictionary containing the status of the health check.
    """

    sns = boto3.client("sns")
    topic_arn = os.environ.get("HEALTHCHECK_ARN")

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return {"status": "healthy", "url": url}

        # Handle bad status codes
        if topic_arn:
            sns.publish(
                TopicArn=topic_arn,
                Message=f"Health check failed for {url}. Status code: {response.status_code}",
                Subject="Health Check Alert",
            )

        return {"status": "unhealthy", "url": url, "code": response.status_code}

    except requests.exceptions.RequestException as e:
        if topic_arn:
            sns.publish(
                TopicArn=topic_arn,
                Message=f"Health check failed for {url}. Error: {str(e)}",
                Subject="Health Check Exception",
            )

        return {"status": "unhealthy", "url": url, "error": str(e)}


# Example usage
if __name__ == "__main__":
    print(health_check())
