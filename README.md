# zettibot-witai
A Telegram bot based on a real person. It is constantly learning by interacting with its users, even right now.

## Build commands!
docker build --network=host -t zettibot-witai . && docker stop zettibot && docker rm zettibot && docker run -d --network=host --restart unless-stopped --name zettibot -v /home/pi/docker/bots/zettibot-witai/feedback:/feedback --env-file .env zettibot-witai
