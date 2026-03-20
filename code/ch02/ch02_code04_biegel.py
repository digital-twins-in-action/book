import base64, requests, argparse


def call_claude_with_image(api_key, image_path, prompt):
    with open(image_path, "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode("utf-8")

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": encoded_image,
                    },
                },
            ],
        }
    ]

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 10000,
            "messages": messages,
        },
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}\n{response.text}")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", "-k", required=True, help="API key")

    args = parser.parse_args()

    response = call_claude_with_image(
        args.api_key,
        "./images/pid.png",
        "I have uploaded a PNG image containing a Process and Instrumentation Diagram (PID). Please convert Convert it to a JSON representation as an array of equipment and connections between the equipment, instruments, lines, and control points.",
    )

    if response:
        print(response["content"][0]["text"])
